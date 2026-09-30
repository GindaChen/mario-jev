"""Check that recorded executed keys only differ by the declared A-release aid."""

import argparse
import json
from pathlib import Path

from mario_jev.policy import ACTIONS


def audit(root):
    decisions = 0
    releases = 0
    for path in sorted((root / "attempts").glob("*/decisions/*.json")):
        row = json.loads(path.read_text())
        choice = row["response"]["answers"]["action"]["choice"]
        state = row["request"]["state"]
        rearm = bool(
            state["mario"]["grounded"] and state["jump_held"] and "A" in ACTIONS[choice]
        )
        expected = [key for key in ACTIONS[choice] if not (rearm and key == "A")]
        assert row["selected_action"] == choice
        assert row["keys"] == expected == ACTIONS[row["action"]]
        assert row["rearm_release"] == rearm
        assert row["requested_frames"] == (1 if rearm else 4)
        assert 1 <= row["executed_frames"] <= row["requested_frames"]
        decisions += 1
        releases += rearm
    if not decisions:
        raise ValueError("No recorded decisions to audit")
    result = {
        "passed": True,
        "decisions_checked": decisions,
        "declared_A_releases": releases,
        "other_action_overrides": 0,
        "rule": "Executed keys equal CLM-selected keys, except remove A for one frame when grounded and A was already held. No coordinate, zone, enemy or elapsed-time input is consulted by this audit rule.",
    }
    (root / "audit/action-authority.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    print(json.dumps(audit(parser.parse_args().root), indent=2))
