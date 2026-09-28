#!/usr/bin/env python3
"""Check the overnight campaign's immutable sources, profiles, and action lineage."""

import argparse
import hashlib
import json
import tarfile
from collections import Counter
from pathlib import Path

from mario_jev.policy import ACTIONS


def audit(root):
    status = json.loads((root / "status.json").read_text())
    trace = root / "trajectory.jsonl"
    errors, profiles, sources, clears = [], {}, set(), []
    counts = Counter()
    previous_sequence = -1
    for line in trace.open():
        row = json.loads(line)
        if row["sequence"] != previous_sequence + 1:
            errors.append(f"Sequence discontinuity: {row['sequence']}")
        previous_sequence = row["sequence"]
        if row["type"] == "config":
            sources.add(row["source_sha256"])
        elif row["type"] == "event":
            counts[row["kind"]] += 1
            if row["kind"] == "stage_start":
                path = root / row["profile"]
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if digest != row["profile_sha256"]:
                    errors.append(f"Profile mismatch: {path}")
                profiles[(row["stage"], row["attempt"])] = digest
            elif row["kind"] == "stage_clear":
                clears.append(row["stage"])
        elif row["type"] == "decision":
            counts["decisions"] += 1
            if row["profile_sha256"] != profiles.get((row["stage"], row["attempt"])):
                errors.append(f"Decision profile mismatch: {row['sequence']}")
            controller = row["controller"]
            selected = controller.get("decisions", {}).get("selected_action")
            if selected is not None:
                counts["direct_model_action_decisions"] += 1
                actual_buttons, chosen_buttons = (
                    set(ACTIONS[row["action"]]),
                    set(ACTIONS[selected]),
                )
                if actual_buttons - chosen_buttons:
                    errors.append(
                        f"Buttons added after model choice: {row['sequence']}"
                    )
                removed = chosen_buttons - actual_buttons
                if removed:
                    counts["jump_release_decisions"] += 1
                    if removed != {"A"} or not controller["decisions"].get(
                        "rearm_release"
                    ):
                        errors.append(f"Unexpected button removal: {row['sequence']}")
            elif controller.get("control_origin") == "cutscene_wait":
                counts["cutscene_wait_decisions"] += 1
            else:
                counts["legacy_threshold_policy_decisions"] += 1
    for sha in sorted(sources):
        digest = hashlib.sha256()
        with tarfile.open(root / "sources" / f"{sha}.tar.gz") as archive:
            for member in archive.getmembers():
                if member.isfile():
                    digest.update(
                        member.name.encode()
                        + b"\0"
                        + archive.extractfile(member).read()
                    )
        if digest.hexdigest() != sha:
            errors.append(f"Source content mismatch: {sha}")
    if clears != status["cleared_stages"]:
        errors.append("Status and recorded clear events disagree")
    if counts["decisions"] != status["total_decisions"]:
        errors.append("Status and recorded decision count disagree")
    if status["status"] == "completed" and clears != status["stage_order"]:
        errors.append("Completed status without every stage in order")
    return {
        "campaign_id": status["campaign_id"],
        "integrity_verified": not errors,
        "errors": errors,
        "trace_sha256": hashlib.sha256(trace.read_bytes()).hexdigest(),
        "profiles_checked": len(profiles),
        "source_snapshots_checked": sorted(sources),
        "counts": dict(counts),
        "cleared_stages": clears,
        "restarts": status["restarts"],
        "mode": status["mode"],
        "limitation": "Integrity is separate from deterministic emulator replay verification. Legacy 1-1 converts model judgments through the existing threshold controller; reflection stages select actions directly with optional A-button release.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    result = audit(args.root)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["integrity_verified"] else 1)
