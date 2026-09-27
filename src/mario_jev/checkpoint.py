"""Reconstruct a pre-failure state by replaying actual recorded inputs."""

from .replay import load_replay


def resume_prefix(path, rewind_frames):
    config, decisions = load_replay(path)
    if config["episodes"] != 1 or any(r["episode"] != 0 for r in decisions):
        raise ValueError("Resume currently requires a single-episode trace")
    target = max(0, sum(r["frames_executed"] for r in decisions) - rewind_frames)
    prefix = []
    elapsed = 0
    for record in decisions:
        if elapsed + record["frames_executed"] > target:
            break
        if record["result"]["terminated"] or record["result"]["truncated"]:
            break
        prefix.append(record)
        elapsed += record["frames_executed"]
    return config, prefix
