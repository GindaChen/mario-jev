"""Summarize complete gameplay traces without treating errors as deaths."""

import argparse
import json
import statistics
from collections import Counter
from pathlib import Path


def summarize(path):
    records = [json.loads(line) for line in path.read_text().splitlines()]
    config = records[0]
    decisions = [r for r in records if r["type"] == "decision"]
    summaries = [r for r in records if r["type"] == "summary"]
    return {
        "trace": str(path),
        "model": config["model"],
        "policy": config["policy"],
        "episodes": summaries,
        "decisions_recorded": len(decisions),
        "complete_trace": len(summaries) == config["episodes"],
        "max_x": max(
            [r["max_x"] for r in summaries] + [r["result"]["x"] for r in decisions],
            default=None,
        ),
        "median_decision_ms": statistics.median(r["latency_ms"] for r in decisions)
        if decisions
        else None,
        "max_input_row_tokens": max(
            (
                max(question["response"]["input_tokens_per_row"])
                for r in decisions
                for question in r.get("backend_diagnostics", {}).values()
                if isinstance(question, dict) and "response" in question
            ),
            default=None,
        ),
        "last_50_actions": dict(Counter(r["action"] for r in decisions[-50:])),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            [summarize(p) for p in sorted(args.directory.glob("*/*.jsonl"))], indent=2
        )
    )
