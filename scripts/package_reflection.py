#!/usr/bin/env python3
"""Package mirrored DJev experiments with exact replay checks and selected videos.

No inference calls or new gameplay are performed: recorded actions are replayed.
"""

import argparse
import contextlib
import csv
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tarfile
from datetime import UTC, datetime
from pathlib import Path


def inspect_trace(path):
    events, malformed = [], []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            if not isinstance(event, dict):
                raise TypeError("JSON record is not an object")
            events.append(event)
        except (json.JSONDecodeError, ValueError, TypeError) as error:
            malformed.append({"line": number, "error": str(error)})
    decisions = [e for e in events if e.get("type") == "decision"]
    summary = next((e for e in reversed(events) if e.get("type") == "summary"), {})
    config = next((e for e in events if e.get("type") == "config"), {})
    return {
        "decisions": len(decisions),
        "malformed_lines": malformed,
        "has_summary": bool(summary),
        "fresh_start": config.get("fresh_start"),
        "completed": summary.get("completed", False),
        "stop_reason": summary.get("stop_reason", "missing_summary"),
        "max_x": summary.get(
            "max_x",
            max((d.get("result", {}).get("x", 0) for d in decisions), default=0),
        ),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def portable_manifest(manifest):
    result = json.loads(json.dumps(manifest))
    for attempt in result["attempts"]:
        directory = Path(attempt["directory"]).name
        attempt["original_directory"] = attempt["directory"]
        attempt["original_profile"] = attempt.get("profile")
        attempt["directory"] = directory
        attempt["profile"] = directory + "/profile.json"
        attempt["profile_snapshot"] = directory + "/profile.json"
    result["sources"] = {
        sha: "sources/" + Path(path).name
        for sha, path in result.get("sources", {}).items()
    }
    result["path_note"] = (
        "Paths are relative to this manifest. Original launch commands retain AMD paths for provenance."
    )
    return result


def choose_videos(rows, maximum):
    eligible = [r for r in rows if r["verification"] == "verified"]
    if not eligible or maximum == 0:
        return []
    selected = []

    def add(row):
        if row not in selected and len(selected) < maximum:
            selected.append(row)

    add(max(eligible, key=lambda r: (bool(r["completed"]), r["max_x"])))
    add(min(eligible, key=lambda r: r["attempt"]))
    for attempt in (81, 82):
        match = next((r for r in eligible if r["attempt"] == attempt), None)
        if match:
            add(match)
    categories = {
        (r["stop_reason"], int(r["max_x"]) // 256)
        for r in selected
        if not r["completed"]
    }
    for row in sorted(eligible, key=lambda r: r["max_x"], reverse=True):
        category = (row["stop_reason"], int(row["max_x"]) // 256)
        if not row["completed"] and category not in categories:
            add(row)
            categories.add(category)
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("runs/djev-reflection-100"))
    parser.add_argument(
        "--output", type=Path, default=Path("deliverables/djev-reflection-100")
    )
    parser.add_argument("--max-videos", type=int, default=6)
    args = parser.parse_args()
    if not 0 <= args.max_videos <= 6:
        parser.error("--max-videos must be between 0 and 6")
    root, output = args.root.resolve(), args.output.resolve()
    if output == root or output.is_relative_to(root):
        parser.error("--output must be outside the source root")
    if output.exists() and any(output.iterdir()):
        parser.error(
            "--output must be absent or empty; existing packages are preserved"
        )
    manifest = json.loads((root / "manifest.json").read_text())
    if any(a.get("status") in ("running", "reserved") for a in manifest["attempts"]):
        parser.error(
            "Experiment has running/reserved attempts; finish the batch before packaging"
        )
    output.mkdir(parents=True, exist_ok=True)
    data = output / "trajectories"
    shutil.copytree(root, data, ignore=shutil.ignore_patterns(".runner.lock", "*.tmp"))
    (data / "manifest.portable.json").write_text(
        json.dumps(portable_manifest(manifest), indent=2) + "\n"
    )
    rows = []
    from mario_jev.replay import replay

    for attempt in manifest["attempts"]:
        directory = data / Path(attempt["directory"]).name
        paths = sorted(directory.glob("*.jsonl"))
        if not paths:
            rows.append(
                {
                    "attempt": attempt["id"],
                    "profile": str(directory.relative_to(output) / "profile.json"),
                    "trace": "",
                    "status": attempt.get("status"),
                    "verification": "missing_trace",
                    "completed": False,
                    "max_x": 0,
                    "stop_reason": "missing_trace",
                    "decisions": 0,
                }
            )
        for path in paths:
            row = {
                "attempt": attempt["id"],
                "profile": str(directory.relative_to(output) / "profile.json"),
                "trace": str(path.relative_to(output)),
                "status": attempt.get("status"),
                **inspect_trace(path),
            }
            capture = io.StringIO()
            if (
                row["malformed_lines"]
                or not row["has_summary"]
                or not row["decisions"]
                or row["status"] != "finished"
            ):
                row["verification"] = "incomplete_or_error"
            else:
                try:
                    with (
                        contextlib.redirect_stdout(capture),
                        contextlib.redirect_stderr(capture),
                    ):
                        replay(path, headless=True, speed=100)
                    if (
                        f"Final episode completed={bool(row['completed'])}"
                        not in capture.getvalue()
                    ):
                        raise ValueError(
                            "Replay completion disagrees with trace summary"
                        )
                    row["verification"] = "verified"
                except Exception as error:  # noqa: BLE001 - preserve every per-trace failure and continue
                    row["verification"] = "failed"
                    row["error"] = f"{type(error).__name__}: {error}"
            log = directory / (path.stem + ".verification.log")
            log.write_text(capture.getvalue())
            rows.append(row)
            print(
                json.dumps(
                    {
                        k: row.get(k)
                        for k in ("attempt", "verification", "max_x", "completed")
                    }
                ),
                flush=True,
            )
    ffmpeg = shutil.which("ffmpeg")
    video_results = []
    repo = Path(__file__).resolve().parents[1]
    for row in choose_videos(rows, args.max_videos) if ffmpeg else []:
        video = (
            output / "videos" / f"{row['attempt']:03d}-{Path(row['trace']).stem}.mp4"
        )
        video.parent.mkdir(exist_ok=True)
        result = subprocess.run(
            [
                sys.executable,
                str(repo / "scripts/export_replay.py"),
                str(output / row["trace"]),
                str(video),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        video.with_suffix(".log").write_text(result.stdout + result.stderr)
        record = {
            "attempt": row["attempt"],
            "trace": row["trace"],
            "returncode": result.returncode,
            "status": "exported" if result.returncode == 0 else "failed",
        }
        if result.returncode == 0:
            record["video"] = str(video.relative_to(output))
        else:
            video.unlink(missing_ok=True)
        video_results.append(record)
    verification = {
        "created_at": datetime.now(UTC).isoformat(),
        "attempts": len(manifest["attempts"]),
        "verified_traces": sum(r["verification"] == "verified" for r in rows),
        "verified_passes": sum(
            r["verification"] == "verified" and bool(r["completed"]) for r in rows
        ),
        "ffmpeg": ffmpeg,
        "videos": video_results,
        "traces": rows,
    }
    (output / "verification.json").write_text(json.dumps(verification, indent=2) + "\n")
    columns = [
        "attempt",
        "status",
        "verification",
        "completed",
        "max_x",
        "stop_reason",
        "decisions",
        "trace",
        "profile",
    ]
    with (output / "index.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# DJev world 1-2 reflection trajectories",
        "",
        f"Attempts: {verification['attempts']}. Verified traces: {verification['verified_traces']}. Verified passes: {verification['verified_passes']}.",
        "",
        "Original manifest is preserved; trajectories/manifest.portable.json uses local relative paths.",
        "",
        "Replay a trace from the Mario project with `.venv/bin/mario-jev --replay /absolute/path/to/trace.jsonl`.",
        "",
        "| Attempt | Max x | Completed | Verification | Trace | Profile |",
        "|---|---:|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['attempt']} | {row['max_x']} | {row['completed']} | {row['verification']} | [trace]({row['trace']}) | [profile]({row['profile']}) |"
        )
    lines += ["", "## Representative videos", ""]
    lines += [
        f"- Attempt {v['attempt']}: [video]({v['video']})"
        if v["status"] == "exported"
        else f"- Attempt {v['attempt']}: video export failed; inspect the video log."
        for v in video_results
    ]
    if not ffmpeg:
        lines.append("ffmpeg was unavailable; no videos exported.")
    lines += [
        "",
        "Incomplete/error traces remain in the bundle but are never counted as verified. Full checks are in verification.json.",
    ]
    (output / "index.md").write_text("\n".join(lines) + "\n")
    archive = output / "djev-reflection-100.tar.gz"
    with tarfile.open(archive, "w:gz") as bundle:
        for path in sorted(output.iterdir()):
            if path != archive:
                bundle.add(path, arcname=path.name)
    print(
        json.dumps(
            {
                "output": str(output),
                "archive": str(archive),
                "verified_traces": verification["verified_traces"],
                "verified_passes": verification["verified_passes"],
            }
        )
    )


if __name__ == "__main__":
    main()
