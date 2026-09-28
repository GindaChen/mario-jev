#!/usr/bin/env python3
"""Frozen-policy, native 1-1 -> 8-4 evaluation; any death restarts at 1-1."""

import argparse
import hashlib
import json
import time
from pathlib import Path

from PIL import Image
from run_campaign import atomic, now
from run_reflection_batch import source_snapshot

from mario_jev.djev import DjevPolicy
from mario_jev.full_game import STAGES, RunProgress, make_full_game, playable
from mario_jev.history import ObservationMemory
from mario_jev.policy import ACTIONS
from mario_jev.reflection import ReflectionDjevPolicy
from mario_jev.runner import frame_position
from mario_jev.situational import SituationalDjevPolicy

REPO = Path(__file__).resolve().parents[1]


def evidence(env, info):
    return {
        "info": json.loads(json.dumps(info)),
        "ram_sha256": hashlib.sha256(env.unwrapped.ram.tobytes()).hexdigest(),
    }


def freeze_profiles(root, overrides):
    """Freeze all instructions before the first run, never refresh mid-evaluation."""
    folder = root / "profiles"
    folder.mkdir()
    manifest = {}
    successful_revisions = {"2-1": "r01", "6-2": "r02", "7-2": "r01"}
    for stage in STAGES:
        source = REPO / "prompts/stages" / stage / "winner.json"
        if stage == "1-1":
            source = REPO / "web/public/data/campaign-research/profiles/1-1-005.json"
        if stage in successful_revisions:
            source = (
                REPO
                / "prompts/campaign"
                / f"{stage}-{successful_revisions[stage]}.json"
            )
        if overrides and (overrides / f"{stage}.json").exists():
            source = overrides / f"{stage}.json"
        content = source.read_bytes()
        json.loads(content)
        (folder / f"{stage}.json").write_bytes(content)
        runtime_path = REPO / "prompts/stages" / stage / "winner-runtime.json"
        runtime = json.loads(runtime_path.read_text()) if runtime_path.exists() else {}
        manifest[stage] = {
            "path": f"profiles/{stage}.json",
            "sha256": hashlib.sha256(content).hexdigest(),
            "frames": max(1, int(runtime.get("frames", 4))),
            "source": str(source),
        }
    return manifest


def freeze_single_profile(root, source, through, frames):
    content = source.read_bytes()
    profile = json.loads(content)
    if (
        profile.get("mode") != "situational"
        or "stage" in profile
        or "stage_guidance" in profile
    ):
        raise ValueError(
            "Single-prompt mode requires a situational profile without stage-specific instructions"
        )
    # Validate the controller schema before beginning any emulator or model call.
    probe = SituationalDjevPolicy("http://localhost", source)
    probe.close()
    folder = root / "profiles"
    folder.mkdir()
    (folder / "single.json").write_bytes(content)
    (folder / "single.json").chmod(0o444)
    row = {
        "path": "profiles/single.json",
        "sha256": hashlib.sha256(content).hexdigest(),
        "frames": frames,
        "source": str(source),
    }
    return {stage: dict(row) for stage in STAGES[: STAGES.index(through) + 1]}


def attempt(root, number, args, profiles):
    folder = root / f"attempt-{number:03d}"
    folder.mkdir()
    started = time.perf_counter()
    progress = RunProgress(getattr(args, "through", "8-4"))
    active_digest = None
    env = policy = None
    frames = decisions = 0
    reason = "frame_limit"
    active_stage = None
    info = {}
    with (folder / "trajectory.jsonl").open("w", buffering=1) as stream:

        def write(row):
            stream.write(json.dumps(row) + "\n")

        try:
            env, info = make_full_game(args.seed)
            write(
                {
                    "type": "reset",
                    "seed": args.seed,
                    "through": progress.through,
                    "boot_actions": env.unwrapped.boot_actions,
                    "result": evidence(env, info),
                }
            )
            while frames < args.max_frames:
                if (root / "STOP").exists():
                    reason = "stopped"
                    break
                if playable(info) and active_stage != progress.stage:
                    active_stage = progress.stage
                    row = profiles[active_stage]
                    path = root / row["path"]
                    if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
                        raise ValueError("Frozen profile changed")
                    profile = json.loads(path.read_text())
                    if policy is None or active_digest != row["sha256"]:
                        if policy:
                            policy.close()
                        cls = {
                            "reflection": ReflectionDjevPolicy,
                            "situational": SituationalDjevPolicy,
                        }.get(profile.get("mode"), DjevPolicy)
                        policy = cls(
                            args.endpoint, profile=path, api_path="/v1/systemone"
                        )
                        active_digest = row["sha256"]
                    memory = ObservationMemory(
                        12,
                        extra_solid_tiles=profile.get("extra_solid_tiles", []),
                        include_room_metadata=profile.get(
                            "include_room_metadata", False
                        ),
                    )
                    write(
                        {
                            "type": "stage_control",
                            "stage": active_stage,
                            "frame": frames,
                            "profile": row,
                        }
                    )
                state = memory.observe(
                    env.unwrapped.ram, info, profiles[active_stage]["frames"]
                )
                call_start = time.perf_counter()
                if playable(info):
                    if decisions >= args.max_decisions:
                        reason = "decision_limit"
                        break
                    action, diagnostics = policy.choose(state)
                    decisions += 1
                    count = max(
                        1,
                        min(
                            profiles[active_stage]["frames"],
                            int(
                                diagnostics.get(
                                    "requested_action_frames",
                                    profiles[active_stage]["frames"],
                                )
                            ),
                        ),
                    )
                    origin = "djev"
                else:
                    action, diagnostics, count, origin = (
                        "wait",
                        {},
                        1,
                        "native_animation_wait",
                    )
                latency = (time.perf_counter() - call_start) * 1000
                reward, samples, signals = 0.0, [], []
                previous_position = frame_position(env.unwrapped.ram)
                outcome = None
                initial_playable = playable(info)
                initial_stage = progress.stage
                for _ in range(min(count, args.max_frames - frames)):
                    before = info
                    _, value, terminated, truncated, info = env.step(
                        list(ACTIONS).index(action)
                    )
                    frames += 1
                    reward += float(value)
                    current = frame_position(env.unwrapped.ram)
                    samples.append(
                        {
                            **current,
                            "frame": len(samples) + 1,
                            "vx_px_per_frame": current["x"] - previous_position["x"],
                            "vy_px_per_frame": current["y"] - previous_position["y"],
                            "landed": not previous_position["grounded"]
                            and current["grounded"],
                        }
                    )
                    signals.append(
                        {
                            "frame": frames,
                            "time": info["time"],
                            "life": info["life"],
                            "world": info["world"],
                            "stage": info["stage"],
                            "player_state": info["player_state"],
                        }
                    )
                    outcome = progress.observe(before, info)
                    if (
                        outcome
                        or terminated
                        or truncated
                        or playable(info) != initial_playable
                        or progress.stage != initial_stage
                        or samples[-1]["landed"]
                    ):
                        if not outcome and (terminated or truncated):
                            outcome = "environment_ended"
                        break
                    previous_position = current
                transition = memory.finish(
                    state,
                    env.unwrapped.ram,
                    info,
                    action,
                    len(samples),
                    reward,
                    bool(outcome),
                    samples=samples,
                )
                write(
                    {
                        "type": "step",
                        "frame": frames,
                        "stage": initial_stage,
                        "origin": origin,
                        "action": action,
                        "frames": len(samples),
                        "state": state if origin == "djev" else None,
                        "controller": diagnostics,
                        "latency_ms": latency,
                        "transition": transition if origin == "djev" else None,
                        "signals": signals,
                        "result": evidence(env, info),
                        "outcome": outcome,
                    }
                )
                if outcome:
                    reason = outcome
                    break
                if decisions % 25 == 0 or progress.stage != initial_stage:
                    Image.fromarray(env.render()).save(root / "latest-frame.jpg")
                    atomic(
                        root / "status.json",
                        {
                            "status": "running",
                            "attempt": number,
                            "stage": progress.stage,
                            "cleared": progress.cleared,
                            "frames": frames,
                            "decisions": decisions,
                            "current": info,
                            "updated_at": now(),
                        },
                    )
        except Exception as exc:  # noqa: BLE001 - persist inference/driver failures for audit
            reason = "error"
            write({"type": "error", "error": f"{type(exc).__name__}: {exc}"})
        finally:
            if policy:
                policy.close()
            if env:
                Image.fromarray(env.render()).save(root / "latest-frame.jpg")
                env.close()
        result = {
            "type": "attempt_end",
            "attempt": number,
            "outcome": reason,
            "cleared": progress.cleared,
            "furthest_stage": progress.stage,
            "frames": frames,
            "decisions": decisions,
            "last_info": info,
            "wall_seconds": time.perf_counter() - started,
        }
        write(result)
        atomic(folder / "result.json", result)
        return result


def replay(path):
    env = None
    frames = 0
    progress = RunProgress()
    outcome = None
    ended = False
    try:
        for line in path.read_text().splitlines():
            row = json.loads(line)
            if row["type"] == "reset":
                if env:
                    raise ValueError("Multiple resets inside one full-game attempt")
                progress = RunProgress(row.get("through", "8-4"))
                env, info = make_full_game(row["seed"])
                assert env.unwrapped.boot_actions == row["boot_actions"]
                assert evidence(env, info) == row["result"]
            elif row["type"] == "step":
                assert env and not ended and outcome is None
                for signal in row["signals"]:
                    before = info
                    _, _, terminated, truncated, info = env.step(
                        list(ACTIONS).index(row["action"])
                    )
                    frames += 1
                    assert signal == {
                        "frame": frames,
                        **{key: info[key] for key in signal if key != "frame"},
                    }
                    outcome = progress.observe(before, info)
                    if not outcome and (terminated or truncated):
                        outcome = "environment_ended"
                assert len(row["signals"]) == row["frames"]
                assert frames == row["frame"]
                assert evidence(env, info) == row["result"], (
                    f"Replay mismatch at frame {frames}"
                )
                assert outcome == row["outcome"]
            elif row["type"] == "attempt_end":
                assert not ended and env
                assert row["frames"] == frames and row["cleared"] == progress.cleared
                assert row["outcome"] == outcome or (
                    outcome is None
                    and row["outcome"]
                    in {"error", "stopped", "decision_limit", "frame_limit"}
                )
                ended = True
        assert ended, "Incomplete trajectory"
        return {
            "verified": True,
            "frames": frames,
            "completed": progress.finished,
            "cleared": progress.cleared,
        }
    finally:
        if env:
            env.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--endpoint", default="http://127.0.0.1:18515")
    parser.add_argument("--overrides", type=Path)
    parser.add_argument(
        "--single-profile",
        type=Path,
        help="One frozen situational prompt for the entire run",
    )
    parser.add_argument(
        "--through",
        choices=STAGES,
        default="8-4",
        help="Last stage to clear; partial runs stop at the next playable stage",
    )
    parser.add_argument("--frames", type=int, default=4)
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("--max-decisions", type=int, default=30000)
    parser.add_argument("--max-frames", type=int, default=300000)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args()
    if args.replay:
        print(json.dumps(replay(args.replay), indent=2))
        return
    if (
        not args.root
        or min(args.attempts, args.max_frames, args.max_decisions, args.frames) < 1
    ):
        parser.error("Supply a new --root and positive evaluation limits")
    if args.single_profile and args.overrides:
        parser.error("--single-profile cannot be combined with stage overrides")
    args.root.mkdir(parents=True, exist_ok=False)
    profiles = (
        freeze_single_profile(args.root, args.single_profile, args.through, args.frames)
        if args.single_profile
        else freeze_profiles(args.root, args.overrides)
    )
    source_sha, source_archive = source_snapshot(REPO, args.root)
    atomic(
        args.root / "config.json",
        {
            "mode": "native_full_game_deathless",
            "through": args.through,
            "single_prompt": bool(args.single_profile),
            "created_at": now(),
            "profiles": profiles,
            "source_sha256": source_sha,
            "source_archive": source_archive,
            "endpoint": args.endpoint,
            "seed": args.seed,
            "attempts": args.attempts,
            "max_frames": args.max_frames,
            "max_decisions": args.max_decisions,
            "timing": "ROM frames include cutscenes; inference pauses simulation; boot frames recorded separately",
        },
    )
    results = []
    for number in range(1, args.attempts + 1):
        result = attempt(args.root, number, args, profiles)
        results.append(result)
        atomic(
            args.root / "status.json",
            {"status": result["outcome"], "attempts": results},
        )
        print(json.dumps(result), flush=True)
        if result["outcome"] != "death":
            break


if __name__ == "__main__":
    main()
