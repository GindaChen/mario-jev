#!/usr/bin/env python3
"""Freeze the first completed fresh run for one stage and verify its replay."""
import argparse
import contextlib
import io
import json
import shutil
import subprocess
from pathlib import Path

from mario_jev.replay import replay

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('stage')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
source = root / 'runs/stages' / args.stage
for trace in sorted(source.rglob('*.jsonl')):
    records = [json.loads(line) for line in trace.read_text().splitlines() if line.strip()]
    summary = next((e for e in reversed(records) if e.get('type') == 'summary'), {})
    if not (summary.get('completed') and summary.get('fresh_start')):
        continue
    assert records[0]['env'] == f'SuperMarioBros-{args.stage}-v0'
    assert not any(e.get('replayed') for e in records)
    import hashlib
    profile = trace.parent / 'profile.json'
    digest = hashlib.sha256(profile.read_bytes()).hexdigest()
    assert all(e['profile_sha256'] == digest for e in records if e['type'] == 'decision')
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        replay(trace, headless=True)
    destination = root / 'deliverables/stages' / args.stage
    destination.mkdir(parents=True, exist_ok=True)
    winner = root / 'prompts/stages' / args.stage / 'winner.json'
    winner.write_bytes(profile.read_bytes())
    runtime = {key: records[0][key] for key in
               ("frames", "decisions", "stall_decisions", "seed", "history", "djev_url")
               if key in records[0]}
    runtime_text = json.dumps(runtime, indent=2) + "\n"
    winner.with_name("winner-runtime.json").write_text(runtime_text)
    (destination / "winning-runtime.json").write_text(runtime_text)
    shutil.copy2(trace, destination / 'winning-trace.jsonl')
    shutil.copy2(profile, destination / 'winning-profile.json')
    (destination / 'replay-verification.txt').write_text(capture.getvalue())
    (destination / 'result.json').write_text(json.dumps({'stage': args.stage, 'trace': str(trace.relative_to(root)), 'profile_sha256': digest, 'trace_sha256': hashlib.sha256(trace.read_bytes()).hexdigest(), 'summary': summary, 'replay_verified': True}, indent=2) + '\n')
    video = destination / 'first-win.mp4'
    if not video.exists():
        subprocess.run([str(root / '.venv/bin/python'), str(root / 'scripts/export_replay.py'), str(trace), str(video)], check=True)
    print(json.dumps({'stage': args.stage, 'completed': True, 'trace': str(trace), 'video': str(video)}))
    break
else:
    raise SystemExit('No completed fresh run; stage remains unpassed')
