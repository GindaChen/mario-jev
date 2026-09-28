#!/usr/bin/env python3
"""Summarize per-stage evidence; only explicit completed summaries count."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
rows = []
for world in range(1, 9):
    for stage in range(1, 5):
        key = f'{world}-{stage}'
        traces = []
        for path in sorted((root / 'runs/stages' / key).rglob('*.jsonl')):
            events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
            summary = next((e for e in reversed(events) if e.get('type') == 'summary'), None)
            if summary:
                traces.append({'trace': str(path.relative_to(root)), **summary})
        wins = [t for t in traces if t.get('completed') and t.get('fresh_start')]
        evidence_path = root / 'deliverables/stages' / key / 'result.json'
        evidence = json.loads(evidence_path.read_text()) if evidence_path.exists() else {}
        evidence_trace = root / evidence.get('trace', '__missing__')
        verified = bool(evidence.get('replay_verified') and
                        evidence.get('summary', {}).get('completed') and
                        evidence_trace.is_file() and
                        hashlib.sha256(evidence_trace.read_bytes()).hexdigest() ==
                        evidence.get('trace_sha256'))
        provenance = evidence.get('provenance', {})
        historical = not traces and verified
        attempts = len(traces) if traces else provenance.get('attempts')
        completed = len(wins) if traces else provenance.get('completed_attempts', 1 if verified else 0)
        rows.append({
            'stage': key,
            'status': 'passed' if verified else 'awaiting_replay' if wins else
                      'attempted' if traces else 'not_run',
            'attempts': attempts,
            'wins': completed,
            'winning_trace': evidence.get('trace') if verified else
                             wins[0]['trace'] if wins else None,
            'max_x': max((t['max_x'] for t in traces),
                         default=evidence.get('summary', {}).get('max_x')),
            'replay_verified': verified,
            'historical_evidence': historical,
            'source_host': evidence.get('source_host', 'AMD' if traces else None),
            'evidence_scope': provenance.get('evidence_scope', 'independent_stage_campaign'),
            'playback_only': evidence.get('playback_only', False),
        })
(root / 'reports/stages/status.json').write_text(json.dumps(rows, indent=2) + '\n')
for row in rows:
    if row['attempts']:
        print(json.dumps(row))

verified_count = sum(row['replay_verified'] for row in rows)
lines = [
    "# Stage campaign progress", "",
    f"**{verified_count}/32 stages replay-verified.** Each stage starts independently; this is not a continuous full-game run.", "",
    ("1-1 uses the prior B200 DJev baseline (recorded replay only; no immutable prompt snapshot). "
    "1-2 uses the closed 100-attempt AMD study. All later stages use AMD-local DJev. "
    "Attempts below count finished gameplay summaries; infrastructure errors remain in the raw manifests."), "",
    "| Stage | Status | Attempts | Completed runs | Host | Replay | Prompt | Audit |",
    "|---|---|---:|---:|---|---|---|---|",
]
for row in rows:
    key = row['stage']
    video = root / "deliverables/stages" / key / "first-win.mp4"
    prompt = root / "prompts/stages" / key / "winner.json"
    audit = root / "reports/stages" / key / "reflection.md"
    if not audit.exists():
        audit = root / "deliverables/stages" / key / "result.json"
    video_link = f"[video]({video})" if video.exists() else ""
    prompt_link = f"[prompt]({prompt})" if prompt.exists() else ""
    audit_link = f"[audit]({audit})" if audit.exists() else ""
    attempts = row['attempts'] if row['attempts'] is not None else 'prior baseline'
    lines.append(f"| {key} | {row['status']} | {attempts} | {row['wins']} | "
                 f"{row['source_host'] or ''} | {video_link} | {prompt_link} | {audit_link} |")
(root / "reports/stages/progress.md").write_text("\n".join(lines) + "\n")
portable = "\n".join(lines).replace(f"]({root}/", "](../")
(root / "deliverables").mkdir(exist_ok=True)
(root / "deliverables/stage-campaign-index.md").write_text(portable + "\n")
