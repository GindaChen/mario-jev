"""Export only reviewed Mario evidence; never publish an experiment directory."""

import argparse
import collections
import difflib
import hashlib
import json
import re
import shutil
from pathlib import Path

SEGMENTS = (
    (
        "corrected",
        "reflection-reviewfix",
        "Corrected reflection",
        "25 attempts · 24 prompt revisions · original deadline",
        "Budget expired during final reflection; raw infra_error retained.",
    ),
    (
        "interrupted",
        "reflection50",
        "Interrupted reflection",
        "3 attempts · reviewer-reference repair",
        "Stopped for the documented false reviewer rejection. Separate from the corrected run.",
    ),
    (
        "baseline",
        "run",
        "Fixed baseline",
        "3 attempts · no System 2",
        "Earlier fixed transfer pilot; outside the reflection budget.",
    ),
)
MANIFEST_FIELDS = (
    "protocol",
    "world",
    "stage",
    "seed",
    "action_frames",
    "landing_interrupt",
    "automatic_grounded_A_release",
    "rearm_frames",
    "upstream_post_step_skips",
    "model",
    "s2_model",
    "s2_reasoning",
    "s2_timeout_s",
    "max_attempts",
    "wall_limit_s",
    "created_unix",
    "reflection_enabled",
    "editable_fields",
    "source_sha256",
    "model_revisions",
    "rom_sha256",
    "checkpoint_ram_sha256",
)
RECORD_FIELDS = (
    "decision",
    "source_frame",
    "result_frame",
    "state",
    "request",
    "response",
    "selected_action",
    "action",
    "rearm_release",
    "keys",
    "requested_frames",
    "executed_frames",
    "latency_ms",
    "samples",
    "before_ram_sha256",
    "after_ram_sha256",
    "info",
    "transition",
    "image_sha256",
    "program_sha256",
)
SECRET = re.compile(
    r'sk-[A-Za-z0-9_-]{20,}|"(?:access_token|refresh_token|id_token|api_key)"\s*:|Bearer\s+[A-Za-z0-9._-]{20,}|eyJ[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{20,}'
)
HOST_PATH = re.compile(r'/(?:Users|home|raid)/[^\s"\'<>]+')


def read(path):
    return json.loads(path.read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def safe_text(text):
    if SECRET.search(text):
        raise ValueError("Possible credential in export; inspect before publishing")
    # Host paths are not part of CLM requests. Only tool-output display is sanitized.
    return HOST_PATH.sub("[host-path]", text)


def check_secrets(value):
    if isinstance(value, str) and SECRET.search(value):
        raise ValueError("Possible credential in export")
    if isinstance(value, dict):
        if {"access_token", "refresh_token", "id_token", "api_key"} & value.keys():
            raise ValueError("Credential field in export")
        for key, item in value.items():
            check_secrets(key)
            check_secrets(item)
    elif isinstance(value, list):
        for item in value:
            check_secrets(item)


def write(path, value):
    check_secrets(value)
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if SECRET.search(text):
        raise ValueError("Possible credential in export")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n")


def source_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Artifact outside experiment root")
    return path


def prompt_diff(before, after):
    return list(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile="before",
            tofile="proposed",
            lineterm="",
        )
    )


def tools_from_log(path):
    """Publish explicit tool actions only, excluding reasoning/session records."""
    if not path.exists():
        return []
    items = {}
    for line in path.read_text().splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {})
        if item.get("type") == "command_execution":
            items[item["id"]] = {
                k: item.get(k)
                for k in (
                    "id",
                    "type",
                    "command",
                    "aggregated_output",
                    "exit_code",
                    "status",
                )
            }
        elif item.get("type") in ("mcp_tool_call", "file_change"):
            raise ValueError("New tool type needs explicit publication review")
    return [
        {k: safe_text(v) if isinstance(v, str) else v for k, v in item.items()}
        for item in items.values()
    ]


def reflection(root, folder, program_versions, outcomes, decision_rows):
    packet = read(folder / "input.json")
    proposal_file = folder / "proposal.json"
    answer_file = folder / "answer.json"
    answer = (
        read(proposal_file if proposal_file.exists() else answer_file)
        if (proposal_file.exists() or answer_file.exists())
        else None
    )
    review_file = folder / "review/answer.json"
    review = read(review_file) if review_file.exists() else None
    published = program_versions.get(str(proposal_file.relative_to(root)))
    source = packet["current_program"]
    criteria_equal = (
        answer["program"]["criteria"] == source["criteria"] if answer else None
    )
    if published is not None:
        state = "published"
    elif answer and (criteria_equal is False or review and not review["allow"]):
        state = "rejected"
    else:
        state = "incomplete"
    reason = (
        review["reason"]
        if review
        else (
            "Frozen candidate descriptions changed; equality validator rejected publication."
            if criteria_equal is False
            else "No completed publication; stopped or timed out. See recorded events."
        )
    )
    published_outcome = (
        next((s for s in outcomes if s["program_version"] == published), None)
        if published is not None
        else None
    )
    rows = decision_rows[-32:]
    return {
        "id": folder.name,
        "status": state,
        "reason": reason,
        "source_attempt": packet["summary"]["attempt_id"],
        "base_version": packet["summary"]["program_version"],
        "published_version": published,
        "next_outcome": published_outcome,
        "proposal": answer,
        "criteria_equal": criteria_equal,
        "review": review,
        "prompt_diff": prompt_diff(
            source["instructions"], answer["program"]["instructions"]
        )
        if answer
        else [],
        "criteria_diff": prompt_diff(
            json.dumps(source["criteria"], indent=2),
            json.dumps(answer["program"]["criteria"], indent=2),
        )
        if answer and not criteria_equal
        else [],
        "request_text": safe_text((folder / "input.txt").read_text()),
        "request_sha256": digest((folder / "input.txt").read_bytes()),
        "packet": packet,
        "attached_images": [
            f"media/{rows[0]['image_sha256']}.jpg",
            f"media/{rows[-1]['image_sha256']}.jpg",
        ],
        "tools": tools_from_log(folder / "stdout.jsonl"),
        "review_request": safe_text((folder / "review/input.txt").read_text())
        if (folder / "review/input.txt").exists()
        else None,
    }


def export(archive, output):
    catalog = {"schema": 1, "title": "Mario 1-2 · CLM reflection audit", "segments": []}
    for sid, dirname, label, subtitle, note in SEGMENTS:
        root = archive / dirname
        manifest = read(root / "manifest.json")
        audit = read(root / "audit/final.json")
        if not audit["passed"]:
            raise ValueError("Cannot publish an unaudited run")
        summaries = [
            read(p) for p in sorted((root / "attempts").glob("*/summary.json"))
        ]
        if {s["attempt_id"] for s in summaries} != {
            a["attempt_id"] for a in audit["attempts"]
        }:
            raise ValueError("Audit coverage differs from completed attempts")
        for name, expected in manifest["source_sha256"].items():
            if (
                digest(source_path(root / "frozen/mario_jev", name).read_bytes())
                != expected
            ):
                raise ValueError("Frozen runtime hash mismatch")
        events = [
            json.loads(l) for l in (root / "events.jsonl").read_text().splitlines()
        ]
        # Only lifecycle fields; no arbitrary error/config dumps.
        public_events = [
            {
                k: e[k]
                for k in (
                    "type",
                    "elapsed_s",
                    "attempt",
                    "version",
                    "reason",
                    "retry",
                    "outcome",
                    "max_x",
                )
                if k in e
            }
            for e in events
        ]
        programs = {
            int(p.name[1:]): read(p / "program.json")
            for p in sorted((root / "programs").iterdir())
        }
        versions = {
            read(p / "provenance.json")["proposal"]: int(p.name[1:])
            for p in (root / "programs").iterdir()
            if (p / "provenance.json").exists()
        }
        baseline_criteria = programs[0]["criteria"]
        assert all(p["criteria"] == baseline_criteria for p in programs.values())
        global_counts = collections.Counter()
        for summary in summaries:
            n = summary["attempt_id"]
            version = summary["program_version"]
            folder = root / f"attempts/{n:04d}"
            rows = sorted(
                (read(p) for p in (folder / "decisions").glob("*.json")),
                key=lambda x: x["decision"],
            )
            if len(rows) != summary["decisions"]:
                raise ValueError("Decision count mismatch")
            shared = rows[0]["request"]["questions"]
            counts = collections.Counter()
            index = []
            for row in rows:
                assert row["request"]["questions"] == shared
                assert row["program_sha256"] == summary["program_sha256"]
                image = source_path(root, row["image"])
                assert digest(image.read_bytes()) == row["image_sha256"]
                media = output / "media" / f"{row['image_sha256']}.jpg"
                media.parent.mkdir(parents=True, exist_ok=True)
                if not media.exists():
                    shutil.copyfile(image, media)
                record = {k: row[k] for k in RECORD_FIELDS}
                record["request_sha256"] = digest(canonical(row["request"]))
                # Exact request values, not a regenerated prompt/state approximation.
                write(
                    output / f"data/{sid}/{n}/decisions/{row['decision']}.json", record
                )
                counts[row["selected_action"]] += 1
                index.append(
                    {
                        k: row[k]
                        for k in (
                            "decision",
                            "source_frame",
                            "result_frame",
                            "selected_action",
                            "action",
                            "latency_ms",
                            "rearm_release",
                            "image_sha256",
                        )
                    }
                    | {"x": row["request"]["state"]["mario"]["x"]}
                )
            global_counts.update(counts)
            summary["selected_action_counts"] = dict(counts)
            refs = [
                reflection(root, p, versions, summaries, rows)
                for p in sorted((root / "reflections").glob(f"{n:04d}*"))
            ]
            proof_path = root / f"audit/replays/{n:04d}.json"
            proof = read(proof_path)
            assert proof["verified"] and proof["frames"] == summary["frames"]
            video = output / f"replay/{sid}-{n}.mp4"
            video.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / f"audit/replays/{n:04d}.mp4", video)
            detail = {
                "summary": summary,
                "program": programs[version],
                "prompt_diff": prompt_diff(
                    programs[version - 1]["instructions"],
                    programs[version]["instructions"],
                )
                if version
                else [],
                "records": index,
                "reflections": refs,
                "events": [e for e in public_events if e.get("attempt") == n],
                "replay": str(video.relative_to(output)),
                "replay_verification": {
                    k: proof[k]
                    for k in ("attempt", "frames", "fps", "duration_s", "verified")
                },
                "built_from": next(
                    (
                        int(Path(key).parts[1].split("-")[0])
                        for key, v in versions.items()
                        if v == version
                    ),
                    None,
                ),
            }
            write(output / f"data/{sid}/{n}/attempt.json", detail)
        stats = {
            "decisions": sum(x["decisions"] for x in summaries),
            "frames": sum(x["frames"] for x in summaries),
            "releases": sum(x["automatic_releases"] for x in summaries),
            "clears": sum(x["native_flag_get"] for x in summaries),
            "best_x": max(x["max_x"] for x in summaries),
            "actions": dict(global_counts),
        }
        catalog["segments"].append(
            {
                "id": sid,
                "label": label,
                "subtitle": subtitle,
                "note": note,
                "attempts": summaries,
                "stats": stats,
                "manifest": {k: manifest[k] for k in MANIFEST_FIELDS if k in manifest},
                "audit": audit,
                "system2_template": (
                    root / "frozen/template/system2-instructions.md"
                ).read_text()
                if (root / "frozen/template/system2-instructions.md").exists()
                else None,
            }
        )
    write(output / "data/catalog.json", catalog)
    return catalog


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = export(args.archive, args.output)
    print(json.dumps({s["id"]: s["stats"] for s in result["segments"]}, indent=2))
