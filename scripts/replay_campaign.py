#!/usr/bin/env python3
"""Verify every campaign action; export all attempts or stitched winning stages."""

import argparse
import json
import subprocess
from pathlib import Path

import gym_super_mario_bros
import numpy as np
from nes_py.wrappers import JoypadSpace
from PIL import Image, ImageDraw
from run_campaign import STAGES, guard_final_cutscene, next_stage, stage_of

from mario_jev.policy import ACTIONS


def records(path):
    with path.open() as stream:
        for line_number, line in enumerate(stream):
            if line.strip():
                yield line_number, json.loads(line)


def index_trace(path):
    """Classify loads using the following stage_start, not the reset reason."""
    loads, winners, seen = {}, {}, set()
    pending = None
    natural_transitions = 0
    for line, record in records(path):
        if record["type"] == "reset":
            pending = line
            loads[line] = {"kind": "unclassified", "stage": record["stage"]}
        elif record["type"] == "event" and record["kind"] == "stage_start":
            stage, attempt = record["stage"], record["attempt"]
            retry = stage in seen or attempt > 1
            if pending is not None:
                if loads[pending]["stage"] != stage:
                    raise ValueError("Reset and following stage_start disagree")
                loads[pending].update(
                    kind="retry" if retry else "stage_load", attempt=attempt
                )
                pending = None
            elif retry:
                raise ValueError("Retry stage_start without an explicit reset")
            else:
                natural_transitions += 1
            seen.add(stage)
        elif record["type"] == "event" and record["kind"] == "stage_clear":
            winners.setdefault(record["stage"], record["attempt"])
    return loads, winners, natural_transitions


def show_attempt(stage, attempt, winners, winning_only):
    return not winning_only or winners.get(stage) == attempt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    parser.add_argument("--video", type=Path)
    parser.add_argument(
        "--winning-only",
        action="store_true",
        help="Video only: stitch successful stage attempts; still verify every action",
    )
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args(argv)
    if args.winning_only and not args.video:
        parser.error("--winning-only requires --video")
    loads, winners, natural_transitions = index_trace(args.trace)
    if args.winning_only and not winners:
        parser.error("No cleared stage attempts to include in winning-only video")
    env = encoder = last = None
    cleared = []
    decisions = retries = video_frames = 0
    complete = False
    if args.video:
        args.video.parent.mkdir(parents=True, exist_ok=True)
        encoder = subprocess.Popen(
            [
                "ffmpeg",
                "-v",
                "error",
                "-n",
                "-f",
                "rawvideo",
                "-pixel_format",
                "rgb24",
                "-video_size",
                "256x280",
                "-framerate",
                "60",
                "-i",
                "pipe:0",
                "-vf",
                "scale=768:840:flags=neighbor",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(args.video),
            ],
            stdin=subprocess.PIPE,
        )

    def frame(image, label):
        nonlocal video_frames
        if not encoder:
            return
        canvas = Image.new("RGB", (256, 280), "black")
        canvas.paste(Image.fromarray(np.asarray(image)), (0, 40))
        draw = ImageDraw.Draw(canvas)
        mode = (
            "Winning stages | STITCHED"
            if args.winning_only
            else "Chronological | ALL ATTEMPTS"
        )
        draw.text((3, 3), mode, fill="white")
        draw.text((3, 21), label, fill="white")
        encoder.stdin.write(canvas.tobytes())
        video_frames += 1

    try:
        pending_label = None
        for line, r in records(args.trace):
            if r["type"] == "reset":
                if env:
                    env.close()
                env = JoypadSpace(
                    gym_super_mario_bros.make(r["env"], render_mode="rgb_array"),
                    list(ACTIONS.values()),
                )
                guard_final_cutscene(env)
                image, _ = env.reset(seed=r["seed"])
                kind = loads[line]["kind"]
                retries += kind == "retry"
                pending_label = {
                    "retry": "RETRY",
                    "stage_load": "STAGE LOAD",
                    "unclassified": "LOAD (no attempt)",
                }[kind]
            elif r["type"] == "event" and r["kind"] == "stage_start":
                if env is None:
                    raise ValueError("Stage start before reset")
                if show_attempt(r["stage"], r["attempt"], winners, args.winning_only):
                    label = f"{pending_label or 'NATURAL NEXT'} {r['stage']} try {r['attempt']}"
                    for _ in range(60):
                        frame(env.render(), label)
                pending_label = None
            elif r["type"] == "decision":
                if env is None:
                    raise ValueError("Decision before reset")
                for _ in range(r["frames_executed"]):
                    image, _, terminated, truncated, raw = env.step(
                        list(ACTIONS).index(r["action"])
                    )
                    if show_attempt(
                        r["stage"], r["attempt"], winners, args.winning_only
                    ):
                        frame(
                            image,
                            f"{r['stage']} try {r['attempt']} | retries {retries}",
                        )
                info = env.unwrapped._get_info()
                actual = {
                    "x": int(info["x_pos"]),
                    "y": int(env.unwrapped.ram[0xCE]),
                    "world": int(info["world"]),
                    "stage": int(info["stage"]),
                    "flag_get": bool(raw.get("flag_get")),
                    "terminated": bool(terminated),
                    "truncated": bool(truncated),
                }
                if actual != r["result"]:
                    raise ValueError(
                        f"Divergence at sequence {r['sequence']}: {actual} != {r['result']}"
                    )
                decisions += 1
                last = r
            elif r["type"] == "event" and r["kind"] == "stage_clear":
                if not last or (last["stage"], last["attempt"]) != (
                    r["stage"],
                    r["attempt"],
                ):
                    raise ValueError("Clear without matching preceding decision")
                if not (
                    last["result"]["flag_get"]
                    or stage_of(last["result"]) == next_stage(r["stage"])
                ):
                    raise ValueError(
                        "Clear lacks completion flag or natural next-stage transition"
                    )
                cleared.append(r["stage"])
            elif r["type"] == "event" and r["kind"] == "campaign_complete":
                complete = True
        if not args.allow_incomplete and (not complete or cleared != STAGES):
            raise ValueError(f"Campaign incomplete: {len(cleared)}/32 verified clears")
        print(
            json.dumps(
                {
                    "replay_verified": True,
                    "decisions": decisions,
                    "environment_loads": len(loads),
                    "stage_loads": sum(
                        load["kind"] == "stage_load" for load in loads.values()
                    ),
                    "retries": retries,
                    "unclassified_loads": sum(
                        load["kind"] == "unclassified" for load in loads.values()
                    ),
                    "natural_stage_transitions": natural_transitions,
                    "video_mode": (
                        "winning_stages_stitched"
                        if args.winning_only
                        else "chronological_all_attempts"
                    )
                    if args.video
                    else None,
                    "video_frames": video_frames,
                    "cleared_stages": cleared,
                    "campaign_complete": complete,
                }
            )
        )
    finally:
        if env:
            env.close()
        if encoder:
            encoder.stdin.close()
            if encoder.wait() != 0:
                raise RuntimeError("Video encoder failed")


if __name__ == "__main__":
    main()
