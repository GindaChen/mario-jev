"""Run bounded, logged episodes; emulator pauses during model calls."""

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from dotenv import load_dotenv

from .history import ObservationMemory
from .policy import ACTIONS, JevPolicy, ScriptedPolicy
from .runner import execute_action


def positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--policy", choices=["jev", "djev", "scorer", "scripted"], default="jev"
    )
    parser.add_argument(
        "--djev-url",
        default="http://127.0.0.1:18341",
        help="DJev API root (normally an SSH tunnel)",
    )
    parser.add_argument(
        "--model",
        default="jev-latest",
        help="Jev model name, or scorer key: laya, kev, nimble, openjev4, openjev35",
    )
    parser.add_argument(
        "--scorer-url",
        default="http://127.0.0.1:18797",
        help="Scorer gateway or direct worker root URL",
    )
    parser.add_argument(
        "--scorer-direct",
        action="store_true",
        help="Use a single worker /score endpoint",
    )
    parser.add_argument(
        "--djev-isolation",
        choices=["independent", "joint"],
        default="independent",
        help="DJev question evaluation (default: independent; four model reads per decision)",
    )
    parser.add_argument(
        "--world", type=int, choices=range(1, 9), default=1, help="World (default: 1)"
    )
    parser.add_argument(
        "--stage",
        type=int,
        choices=range(1, 5),
        default=1,
        help="Stage within the world (default: 1)",
    )
    parser.add_argument("--frames", type=positive, default=4)
    parser.add_argument(
        "--decisions",
        type=positive,
        default=500,
        help="Maximum decisions per episode (and API calls with Jev)",
    )
    parser.add_argument("--episodes", type=positive, default=1)
    parser.add_argument(
        "--history",
        type=positive,
        default=12,
        help="Recent transitions to send to Jev (default: 12)",
    )
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--log-dir", type=Path, default=Path("runs"))
    parser.add_argument(
        "--log-every",
        type=positive,
        default=25,
        help="Print progress every N decisions, starting at 0 (default: 25); traces retain every decision",
    )
    parser.add_argument(
        "--dump-state",
        action="store_true",
        help="Print initial RAM-derived state without model calls",
    )
    parser.add_argument(
        "--replay", type=Path, help="Replay a gameplay log without API calls"
    )
    parser.add_argument(
        "--speed", type=positive, default=1, help="Replay speed multiplier (default: 1)"
    )
    args = parser.parse_args()
    env_id = f"SuperMarioBros-{args.world}-{args.stage}-v0"
    if args.replay:
        from .replay import replay

        try:
            replay(args.replay, args.headless, args.speed)
        except KeyboardInterrupt:
            print("Replay stopped.")
        except Exception as exc:  # noqa: BLE001 -- CLI error boundary
            parser.exit(1, f"Replay failed ({type(exc).__name__}): {exc}\n")
        return
    load_dotenv()
    if (
        args.policy == "jev"
        and not args.dump_state
        and not os.getenv("TYPESAFE_API_KEY", "").strip()
    ):
        parser.error(
            "Set TYPESAFE_API_KEY in .env or your environment, or use --policy scripted"
        )

    import gym_super_mario_bros
    from nes_py.wrappers import JoypadSpace

    env = None
    policy = None
    try:
        env = JoypadSpace(
            gym_super_mario_bros.make(
                env_id,
                render_mode="rgb_array" if args.headless else "human",
            ),
            list(ACTIONS.values()),
        )
        if args.dump_state:
            _, info = env.reset(seed=args.seed)
            print(
                json.dumps(
                    ObservationMemory(args.history).observe(
                        env.unwrapped.ram, info, args.frames
                    ),
                    indent=2,
                )
            )
            return
        if args.policy == "djev":
            from .djev import DjevPolicy

            policy = DjevPolicy(args.djev_url, isolation=args.djev_isolation)
        elif args.policy == "scorer":
            from .scorer import ScorerPolicy

            policy = ScorerPolicy(
                args.scorer_url, args.model, direct=args.scorer_direct
            )
        else:
            policy = JevPolicy(args.model) if args.policy == "jev" else ScriptedPolicy()
        args.log_dir.mkdir(parents=True, exist_ok=True)
        path = args.log_dir / (
            datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ") + ".jsonl"
        )
        print(f"Logging to {path.resolve()}")
        with path.open("w") as log:

            def write(record):
                log.write(json.dumps(record) + "\n")
                log.flush()

            write(
                {
                    "type": "config",
                    "policy": args.policy,
                    "model": "djev" if args.policy == "djev" else args.model,
                    "djev_url": args.djev_url if args.policy == "djev" else None,
                    "djev_isolation": args.djev_isolation
                    if args.policy == "djev"
                    else None,
                    "scorer_url": args.scorer_url if args.policy == "scorer" else None,
                    "scorer_direct": args.scorer_direct
                    if args.policy == "scorer"
                    else None,
                    "frames": args.frames,
                    "decisions": args.decisions,
                    "episodes": args.episodes,
                    "history": args.history,
                    "interrupt_on_landing": True,
                    "seed": args.seed,
                    "env": env_id,
                }
            )
            for episode in range(args.episodes):
                _, info = env.reset(seed=args.seed + episode)
                if not args.headless:
                    env.render()
                    if episode == 0:
                        # nes-py exposes its pyglet window through the viewer.
                        env.unwrapped.viewer._window.set_size(800, 600)
                        env.render()
                memory = ObservationMemory(args.history)
                max_x = int(info["x_pos"])
                total_reward = 0.0
                completed = False
                terminated = truncated = False
                for decision in range(args.decisions):
                    state = memory.observe(env.unwrapped.ram, info, args.frames)
                    started = perf_counter()
                    action, diagnostics = policy.choose(state)
                    latency = (perf_counter() - started) * 1000
                    info, reward, terminated, truncated, samples = execute_action(
                        env, action, args.frames, args.headless
                    )
                    executed = len(samples)
                    max_x = max(max_x, *(sample["x"] for sample in samples))
                    completed |= bool(info.get("flag_get"))
                    transition = memory.finish(
                        state,
                        env.unwrapped.ram,
                        info,
                        action,
                        executed,
                        reward,
                        terminated or truncated,
                        samples=samples,
                    )
                    total_reward += reward
                    write(
                        {
                            "type": "decision",
                            "episode": episode,
                            "decision": decision,
                            "state": state,
                            "action": action,
                            "latency_ms": round(latency, 2),
                            "frames_executed": executed,
                            "transition": transition,
                            "reward": reward,
                            "result": {
                                "x": int(info["x_pos"]),
                                "y": int(env.unwrapped.ram[0xCE]),
                                "flag_get": completed,
                                "terminated": bool(terminated),
                                "truncated": bool(truncated),
                            },
                            **diagnostics,
                        }
                    )
                    if decision % args.log_every == 0:
                        print(
                            f"Episode {episode + 1}, decision {decision}: x={info['x_pos']} action={action} latency={latency:.0f}ms"
                        )
                    if terminated or truncated:
                        break
                summary = {
                    "type": "summary",
                    "episode": episode,
                    "decisions": decision + 1,
                    "max_x": max_x,
                    "completed": completed,
                    "reward": total_reward,
                    "stop_reason": "completed"
                    if completed
                    else "terminated"
                    if terminated
                    else "truncated"
                    if truncated
                    else "decision_limit",
                }
                write(summary)
                print(json.dumps(summary))
    except KeyboardInterrupt:
        print("Stopped.")
    except Exception as exc:  # noqa: BLE001 -- CLI boundary provides a concise error
        parser.exit(1, f"Mario run failed ({type(exc).__name__}): {exc}\n")
    finally:
        if policy is not None:
            policy.close()
        if env is not None:
            env.close()
