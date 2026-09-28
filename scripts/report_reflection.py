#!/usr/bin/env python3
"""Summarize preserved reflection experiments, including partial/error traces."""

import argparse
import json
import statistics
from pathlib import Path


def read_events(path):
    events, errors = [], 0
    for line in path.read_text().splitlines():
        try:
            event = json.loads(line)
            if isinstance(event, dict):
                events.append(event)
        except json.JSONDecodeError:
            errors += 1
    return events, errors


def summarize(attempt):
    row = {
        key: attempt.get(key)
        for key in (
            "id",
            "profile",
            "profile_sha256",
            "source_sha256",
            "status",
            "returncode",
            "frames",
            "directory",
        )
    }
    traces = []
    for path in sorted(Path(attempt["directory"]).glob("*.jsonl")):
        events, errors = read_events(path)
        decisions = [e for e in events if e.get("type") == "decision"]
        summary = next((e for e in reversed(events) if e.get("type") == "summary"), {})
        config = next((e for e in events if e.get("type") == "config"), {})
        latencies = sorted(
            d["latency_ms"]
            for d in decisions
            if isinstance(d.get("latency_ms"), (int, float))
        )
        detail = []
        for decision in decisions[-20:]:
            state = decision.get("state", {})
            detail.append(
                {
                    key: decision.get(key)
                    for key in (
                        "decision",
                        "action",
                        "result",
                        "transition",
                        "latency_ms",
                    )
                }
                | {
                    "mario": state.get("mario"),
                    "nearest_threat": state.get("nearest_threat"),
                    "terrain": state.get("terrain", {}).get("summary"),
                    "current_jump": state.get("current_jump"),
                    "model_decisions": decision.get("decisions"),
                    "backend_diagnostics": decision.get("backend_diagnostics"),
                }
            )
        traces.append(
            {
                "trace": str(path),
                "decisions": len(decisions),
                "malformed_lines": errors,
                "fresh_start": config.get("fresh_start"),
                "completed": bool(summary.get("completed", False)),
                "stop_reason": summary.get("stop_reason", "no_summary"),
                "max_x": summary.get(
                    "max_x",
                    max(
                        (d.get("result", {}).get("x", 0) for d in decisions), default=0
                    ),
                ),
                "latency_ms": {
                    "mean": statistics.mean(latencies) if latencies else None,
                    "p50": statistics.median(latencies) if latencies else None,
                    "p95": latencies[
                        min(len(latencies) - 1, int(len(latencies) * 0.95))
                    ]
                    if latencies
                    else None,
                },
                "last20_decisions": detail,
            }
        )
    row["traces"] = traces
    row["max_x"] = max((t["max_x"] for t in traces), default=0)
    row["completed"] = any(t["completed"] for t in traces)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("runs/djev-reflection-100"))
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = json.loads((root / "manifest.json").read_text())
    rows = [summarize(a) for a in manifest["attempts"]]
    result = {
        "reserved": len(rows),
        "budget": 100,
        "passes": sum(r["completed"] for r in rows),
        "attempts": rows,
    }
    (root / "report.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = [
        "# DJev reflection experiments",
        "",
        f"Reserved: {len(rows)}/100. Passes: {result['passes']}.",
        "",
        "| Attempt | Profile | Status | Max x | Pass | Trace |",
        "|---|---|---|---:|---|---|",
    ]
    for row in rows:
        trace = ", ".join(
            f"[{Path(t['trace']).name}]({t['trace']})" for t in row["traces"]
        )
        lines.append(
            f"| {row['id']} | {Path(row['profile']).stem} | {row['status']} | {row['max_x']} | {row['completed']} | {trace} |"
        )
    lines += [
        "",
        "Detailed last-20 decisions, latency, request diagnostics, and partial-trace errors are in report.json.",
    ]
    (root / "report.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({key: result[key] for key in ("reserved", "budget", "passes")}))


if __name__ == "__main__":
    main()
