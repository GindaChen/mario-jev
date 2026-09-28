#!/usr/bin/env python3
"""Live DJev campaign: natural transitions first, explicit stage restarts on failure."""

import argparse
import hashlib
import json
import os
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path

import gym_super_mario_bros
from nes_py.wrappers import JoypadSpace
from PIL import Image

from mario_jev.djev import DjevPolicy
from mario_jev.history import ObservationMemory
from mario_jev.policy import ACTIONS
from mario_jev.reflection import ReflectionDjevPolicy
from mario_jev.runner import frame_position

STAGES = [f"{w}-{s}" for w in range(1, 9) for s in range(1, 5)]


def now():
    return datetime.now(UTC).isoformat()


def atomic(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2) + "\n")
    tmp.replace(path)


def stage_of(info):
    return f"{info['world']}-{info['stage']}"


def next_stage(stage):
    index = STAGES.index(stage) + 1
    return STAGES[index] if index < len(STAGES) else None


def guard_final_cutscene(env):
    """Avoid the upstream infinite final-world skip; do not alter RAM or controls."""
    original = env.unwrapped._did_step

    def did_step(done):
        game = env.unwrapped
        if game._world == 8 and game._stage == 4 and game._flag_get:
            return
        original(done)

    env.unwrapped._did_step = did_step


def execute_campaign_action(env, action, frames):
    """Observe post-cutscene RAM, retain raw death/clear signals, never cross a boundary."""
    previous = frame_position(env.unwrapped.ram)
    initial = env.unwrapped._get_info()
    samples = []
    reward = 0.0
    for index in range(frames):
        _, value, terminated, truncated, raw_info = env.step(
            list(ACTIONS).index(action)
        )
        reward += float(value)
        info = env.unwrapped._get_info()
        current = frame_position(env.unwrapped.ram)
        samples.append(
            {
                **current,
                "frame": index + 1,
                "vx_px_per_frame": current["x"] - previous["x"],
                "vy_px_per_frame": current["y"] - previous["y"],
                "landed": not previous["grounded"] and current["grounded"],
            }
        )
        boundary = (
            stage_of(info) != stage_of(initial)
            or info.get("life") != initial.get("life")
            or raw_info.get("flag_get")
            or raw_info.get("is_dead")
            or raw_info.get("is_dying")
            or info.get("is_game_over")
        )
        if terminated or truncated or boundary or samples[-1]["landed"]:
            break
        previous = current
    return info, raw_info, reward, terminated, truncated, samples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("runs/overnight-campaign"))
    parser.add_argument(
        "--endpoints",
        nargs="+",
        default=[
            "http://127.0.0.1:18515",
            "http://127.0.0.1:18516",
            "http://127.0.0.1:18517",
            "http://127.0.0.1:18518",
        ],
    )
    parser.add_argument("--reflection-every", type=int, default=5)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--start-stage", choices=STAGES, default="1-1")
    parser.add_argument("--max-decisions", type=int, default=2500)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Continue the saved ledger with an explicit current-stage reset",
    )
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    os.chdir(repo)
    root = args.root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    import fcntl

    lock = (root / ".lock").open("a")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    previous_status = None
    if (root / "status.json").exists():
        if not args.resume:
            raise SystemExit("Existing campaign: use --resume to preserve history.")
        previous_status = json.loads((root / "status.json").read_text())
        if previous_status["status"] == "completed":
            return
    (root / "profiles").mkdir(exist_ok=True)
    (root / "overrides").mkdir(exist_ok=True)
    from run_reflection_batch import source_snapshot

    source_sha, source_archive = source_snapshot(repo, root)
    status = {
        "schema_version": 1,
        "campaign_id": root.name + "-" + now(),
        "status": "running",
        "mode": "continuous",
        "started_at": now(),
        "updated_at": now(),
        "current_stage": args.start_stage,
        "current_attempt": 0,
        "checkpoint": None,
        "stage_order": STAGES,
        "cleared_stages": [],
        "stage_results": {
            s: {
                "status": "pending",
                "attempts": 0,
                "retries": 0,
                "checkpoint_retries": 0,
                "completed_at": None,
            }
            for s in STAGES
        },
        "restarts": 0,
        "total_decisions": 0,
        "current": {},
        "event_log": [],
        "counts": {},
        "source_sha256": source_sha,
        "source_archive": source_archive,
        "limitation": "The emulator pauses for inference. Resets and automatic cutscene skipping are recorded; this is not a real-time speedrun benchmark.",
    }
    if previous_status:
        status = previous_status
        status["status"] = "running"
        status["mode"] = "stage_linked"
        status["restarts"] += 1
        status["stage_results"][status["current_stage"]]["retries"] += 1
        if status["current_stage"] in status["cleared_stages"]:
            status["current_stage"] = next(
                s for s in STAGES if s not in status["cleared_stages"]
            )
        args.start_stage = status["current_stage"]
    stream = (root / "trajectory.jsonl").open("a", buffering=1)
    policy = env = None
    sequence = 0
    if previous_status:
        recorded_decisions = 0
        with (root / "trajectory.jsonl").open() as existing:
            for line in existing:
                if line.strip():
                    record = json.loads(line)
                    sequence = max(sequence, record["sequence"] + 1)
                    recorded_decisions += record["type"] == "decision"
        # The append-only trace can be ahead of the periodically published status
        # if the previous worker was interrupted between status updates.
        status["total_decisions"] = recorded_decisions

    def write(event):
        nonlocal sequence
        event = {"sequence": sequence, "at": now(), **event}
        stream.write(json.dumps(event) + "\n")
        sequence += 1

    def event(kind, message, **extra):
        item = dict(
            at=now(),
            kind=kind,
            stage=status["current_stage"],
            attempt=status["current_attempt"],
            message=message,
            **extra,
        )
        status["event_log"].append(item)
        status["event_log"] = status["event_log"][-120:]
        write(dict(type="event", **item))

    def publish():
        status["updated_at"] = now()
        status["counts"] = {
            "cleared": len(status["cleared_stages"]),
            "stages": 32,
            "restarts": status["restarts"],
            "total_decisions": status["total_decisions"],
        }
        atomic(root / "status.json", status)

    def make_env(stage, continuous=False):
        nonlocal env
        if env:
            env.close()
        name = "SuperMarioBros-v0" if continuous else f"SuperMarioBros-{stage}-v0"
        env = JoypadSpace(
            gym_super_mario_bros.make(name, render_mode="rgb_array"),
            list(ACTIONS.values()),
        )
        guard_final_cutscene(env)
        _, info = env.reset(seed=args.seed)
        write(
            {
                "type": "reset",
                "env": name,
                "seed": args.seed,
                "stage": stage,
                "reason": "campaign_start"
                if status["total_decisions"] == 0
                else "explicit_stage_loader",
            }
        )
        return info

    def begin(stage):
        nonlocal policy
        if policy:
            policy.close()
        status["current_stage"] = stage
        row = status["stage_results"][stage]
        row["attempts"] += 1
        row["status"] = "running"
        status["current_attempt"] = row["attempts"]
        base = root / "overrides" / f"{stage}.json"
        if not base.exists():
            base = repo / "prompts/stages" / stage / "winner.json"
        endpoint = args.endpoints[(row["attempts"] - 1) % len(args.endpoints)]
        runtime_path = repo / "prompts/stages" / stage / "winner-runtime.json"
        runtime = json.loads(runtime_path.read_text()) if runtime_path.exists() else {}
        frames = runtime.get("frames", 4)
        if base.exists():
            data = base.read_bytes()
            profile = json.loads(data)
            snapshot = root / "profiles" / f"{stage}-{row['attempts']:03d}.json"
            snapshot.write_bytes(data)
            cls = (
                ReflectionDjevPolicy
                if profile.get("mode") == "reflection"
                else DjevPolicy
            )
            if cls is ReflectionDjevPolicy:
                policy = cls(endpoint, snapshot, api_path="/v1/systemone")
            else:
                policy = cls(endpoint, profile=snapshot, api_path="/v1/systemone")
        else:
            if stage != "1-1":
                raise ValueError(f"Missing profile {stage}")
            policy = DjevPolicy(endpoint, api_path="/v1/systemone")
            profile = {
                "name": "campaign-1-1-current-default",
                "questions": {
                    k: {
                        "instructions": v.instructions,
                        **({"criteria": v.criteria} if hasattr(v, "criteria") else {}),
                    }
                    for k, v in policy.questions.items()
                },
            }
            snapshot = root / "profiles" / f"{stage}-{row['attempts']:03d}.json"
            snapshot.write_text(json.dumps(profile, indent=2) + "\n")
        digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
        memory = ObservationMemory(
            12,
            extra_solid_tiles=profile.get("extra_solid_tiles", []),
            include_room_metadata=profile.get("include_room_metadata", False),
        )
        event(
            "stage_start",
            f"Live DJev attempt {row['attempts']} on {stage}.",
            profile=str(snapshot.relative_to(root)),
            profile_sha256=digest,
            endpoint=endpoint,
            frames=frames,
        )
        return memory, frames, runtime.get("stall_decisions", 600), digest

    def clear(stage, evidence):
        if stage not in status["cleared_stages"]:
            status["cleared_stages"].append(stage)
            status["stage_results"][stage].update(status="cleared", completed_at=now())
            event("stage_clear", f"{stage} cleared: {evidence}.")
            publish()

    def reflection_gate(stage):
        row = status["stage_results"][stage]
        if row["retries"] % args.reflection_every:
            return
        status["status"] = "needs_reflection"
        event(
            "reflection_needed",
            f"{row['retries']} failed attempts; review traces and supply a revised profile or explicit continue command.",
        )
        publish()
        command = root / "continue.json"
        if command.exists():
            command.unlink()
        override = root / "overrides" / f"{stage}.json"
        before = override.read_bytes() if override.exists() else None
        while True:
            if command.exists():
                command.unlink()
                break
            if override.exists() and override.read_bytes() != before:
                break
            time.sleep(5)
            publish()
        status["status"] = "running"
        event(
            "reflection_resumed",
            "Supervisor supplied a revision or approved the next batch.",
        )

    try:
        write(
            {
                "type": "config",
                "schema_version": 1,
                "seed": args.seed,
                "policy": "djev",
                "stage_order": STAGES,
                "source_sha256": source_sha,
            }
        )
        stage = args.start_stage
        continuous = stage == "1-1"
        if not continuous:
            status["mode"] = "stage_linked"
        info = make_env(stage, continuous)
        memory, frames, stall_limit, digest = begin(stage)
        local_decisions = stall = 0
        high_x = int(info["x_pos"])
        transitioning = False
        transition_frames = 0
        publish()
        while status["status"] != "completed":
            if (root / "STOP").exists():
                status["status"] = "paused"
                event("paused", "STOP file requested pause.")
                break
            state = memory.observe(env.unwrapped.ram, info, frames)
            started = time.perf_counter()
            if transitioning:
                action, diagnostics = "wait", {"control_origin": "cutscene_wait"}
                count = 16
            else:
                action, diagnostics = policy.choose(state)
                count = max(
                    1, min(frames, diagnostics.get("requested_action_frames", frames))
                )
            latency = (time.perf_counter() - started) * 1000
            previous_info = dict(info)
            info, raw_info, reward, terminated, truncated, samples = (
                execute_campaign_action(env, action, count)
            )
            transition = memory.finish(
                state,
                env.unwrapped.ram,
                info,
                action,
                len(samples),
                reward,
                terminated or truncated,
                samples=samples,
            )
            observed_stage = stage_of(info)
            write(
                {
                    "type": "decision",
                    "stage": stage,
                    "attempt": status["current_attempt"],
                    "decision": local_decisions,
                    "state": state,
                    "action": action,
                    "frames_executed": len(samples),
                    "latency_ms": round(latency, 2),
                    "controller": diagnostics,
                    "profile_sha256": digest,
                    "transition": transition,
                    "result": {
                        "x": int(info["x_pos"]),
                        "y": int(env.unwrapped.ram[0xCE]),
                        "world": int(info["world"]),
                        "stage": int(info["stage"]),
                        "flag_get": bool(raw_info.get("flag_get")),
                        "terminated": bool(terminated),
                        "truncated": bool(truncated),
                    },
                }
            )
            status["total_decisions"] += 1
            local_decisions += 1
            status["current"] = {
                "decision": local_decisions,
                "x": int(info["x_pos"]),
                "room": state.get("room"),
                "latency_ms": round(latency, 2),
                "action": action,
            }
            if local_decisions % 10 == 0 or info.get("flag_get"):
                frame = env.render()
                tmp = root / "latest-frame.tmp.jpg"
                Image.fromarray(frame).save(tmp, quality=85)
                tmp.replace(root / "latest-frame.jpg")
                publish()
            if stage == "8-4" and raw_info.get("flag_get"):
                clear(stage, "final axe completion flag")
                status["status"] = "completed"
                event(
                    "campaign_complete",
                    "Reached the final axe after all scheduled stages.",
                )
                break
            if continuous and observed_stage != stage:
                if observed_stage != next_stage(stage):
                    raise ValueError(
                        f"Unexpected stage transition {stage} -> {observed_stage}; no warp credit."
                    )
                clear(stage, "natural stage transition")
                stage = observed_stage
                memory, frames, stall_limit, digest = begin(stage)
                local_decisions = stall = 0
                high_x = int(info["x_pos"])
                transitioning = False
                transition_frames = 0
                continue
            if raw_info.get("flag_get"):
                clear(stage, "game completion flag")
                if stage == "8-4":
                    status["status"] = "completed"
                    event(
                        "campaign_complete",
                        "Reached the final axe after all scheduled stages.",
                    )
                    break
                if continuous:
                    transitioning = True
                else:
                    stage = next_stage(stage)
                    info = make_env(stage)
                    memory, frames, stall_limit, digest = begin(stage)
                    local_decisions = stall = 0
                    high_x = int(info["x_pos"])
                    continue
            if transitioning:
                transition_frames += len(samples)
                if transition_frames > 4000:
                    raise RuntimeError("Stage transition did not finish")
                continue
            x = int(info["x_pos"])
            room_changed = info.get("area") != previous_info.get("area")
            stall = 0 if x > high_x or room_changed else stall + 1
            high_x = x if room_changed else max(high_x, x)
            died = bool(
                raw_info.get("is_dead")
                or raw_info.get("is_dying")
                or info.get("is_dead")
                or info.get("is_dying")
                or info.get("is_game_over")
                or info.get("life", 99) < previous_info.get("life", 99)
            )
            reason = (
                "death"
                if died or terminated
                else "timeout"
                if truncated
                else "stalled"
                if stall >= stall_limit
                else "decision_limit"
                if local_decisions >= args.max_decisions
                else None
            )
            if reason:
                row = status["stage_results"][stage]
                row["retries"] += 1
                status["restarts"] += 1
                event(
                    "stage_failure",
                    f"{reason}; restarting {stage} from its beginning.",
                    x=x,
                )
                status["mode"] = "stage_linked"
                reflection_gate(stage)
                continuous = False
                info = make_env(stage)
                memory, frames, stall_limit, digest = begin(stage)
                local_decisions = stall = 0
                high_x = int(info["x_pos"])
                transitioning = False
        publish()
    except Exception as exc:
        status["status"] = "error"
        event("error", f"{type(exc).__name__}: {exc}")
        publish()
        traceback.print_exc()
        raise
    finally:
        if policy:
            policy.close()
        if env:
            env.close()
        stream.close()


if __name__ == "__main__":
    main()
