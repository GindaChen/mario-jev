#!/usr/bin/env python3
"""Prepare or run separate, bounded 1-1/1-2/1-3 policy evaluations."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="New output folder; never reuse old results",
    )
    parser.add_argument(
        "--stages",
        nargs="+",
        choices=["1-1", "1-2", "1-3"],
        default=["1-1", "1-2", "1-3"],
    )
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--endpoint", default="http://127.0.0.1:18515")
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Freeze profiles and print commands without inference",
    )
    args = parser.parse_args()
    if args.repeats < 1 or len(set(args.stages)) != len(args.stages):
        parser.error("Use positive repeats and distinct stages")
    root = args.root.resolve()
    root.mkdir(parents=True, exist_ok=False)
    (root / "profiles").mkdir()
    plan = {
        "mode": "independent_stage_development",
        "seed": 123,
        "total_attempt_limit": args.repeats * len(args.stages),
        "stages": [],
    }
    for stage in args.stages:
        data = (REPO / "prompts/situational/world1" / f"{stage}-v1.json").read_bytes()
        profile = root / "profiles" / f"{stage}.json"
        profile.write_bytes(data)
        profile.chmod(0o444)
        command = [
            sys.executable,
            str(REPO / "scripts/run_reflection_batch.py"),
            "--root",
            str(root / stage),
            "--profiles",
            str(profile),
            "--repeats",
            str(args.repeats),
            "--max-attempts",
            str(args.repeats),
            "--workers",
            "1",
            "--world",
            "1",
            "--stage",
            stage[-1],
            "--frames",
            "4",
            "--stall-decisions",
            "150",
            "--djev-url",
            args.endpoint,
        ]
        plan["stages"].append(
            {
                "stage": stage,
                "profile_sha256": hashlib.sha256(data).hexdigest(),
                "command": command,
                "status": "prepared",
            }
        )
    path = root / "plan.json"
    path.write_text(json.dumps(plan, indent=2) + "\n")
    if args.prepare_only:
        print(path)
        return
    for row in plan["stages"]:
        row["status"] = "running"
        path.write_text(json.dumps(plan, indent=2) + "\n")
        result = subprocess.run(
            row["command"],
            cwd=REPO,
            env={**os.environ, "PYTHONPATH": str(REPO / "src")},
            check=False,
        )
        row["status"] = "finished" if result.returncode == 0 else "runner_error"
        row["returncode"] = result.returncode
        path.write_text(json.dumps(plan, indent=2) + "\n")
        if result.returncode:
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
