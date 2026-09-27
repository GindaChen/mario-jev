"""Encode an exact action replay as MP4; no model calls or emulator-state edits."""

import argparse
import subprocess
from pathlib import Path

import gym_super_mario_bros
from nes_py.wrappers import JoypadSpace

from mario_jev.policy import ACTIONS
from mario_jev.replay import load_replay

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("trace", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
config, records = load_replay(args.trace)
if config["episodes"] != 1:
    parser.error("Video export currently supports one episode")
args.output.parent.mkdir(parents=True, exist_ok=True)
env = JoypadSpace(
    gym_super_mario_bros.make(config["env"], render_mode="rgb_array"),
    list(ACTIONS.values()),
)
encoder = None
try:
    frame, _ = env.reset(seed=config["seed"])
    height, width = frame.shape[:2]
    command = [
        "ffmpeg",
        "-v",
        "error",
        "-n",
        "-f",
        "rawvideo",
        "-pixel_format",
        "rgb24",
        "-video_size",
        f"{width}x{height}",
        "-framerate",
        "60",
        "-i",
        "pipe:0",
        "-vf",
        "scale=768:-2:flags=neighbor",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(args.output),
    ]
    encoder = subprocess.Popen(command, stdin=subprocess.PIPE)
    for record in records:
        for _ in range(record["frames_executed"]):
            frame, _, _, _, info = env.step(list(ACTIONS).index(record["action"]))
            encoder.stdin.write(frame.tobytes())
        if (
            int(info["x_pos"]) != record["result"]["x"]
            or int(env.unwrapped.ram[0xCE]) != record["result"]["y"]
        ):
            raise ValueError(f"Replay diverged at {record['decision']}")
    encoder.stdin.close()
    if encoder.wait() != 0:
        raise RuntimeError("Video encoder failed")
    print(args.output.resolve())
finally:
    env.close()
    if encoder is not None and encoder.poll() is None:
        encoder.terminate()
        encoder.wait()
