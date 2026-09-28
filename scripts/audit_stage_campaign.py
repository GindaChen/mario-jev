#!/usr/bin/env python3
"""Read-only integrity audit of campaign reservations and immutable snapshots."""
import hashlib
import json
import tarfile
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest_paths = sorted((root / 'runs/stages').rglob('manifest.json'))
legacy = root / 'runs/djev-reflection-100/manifest.json'
if legacy.exists():
    manifest_paths.append(legacy)
rows, errors, checked_sources = [], [], set()
for manifest_path in manifest_paths:
    manifest = json.loads(manifest_path.read_text())
    for attempt in manifest.get('attempts', []):
        folder = manifest_path.parent / Path(attempt['directory']).name
        row = {'manifest': str(manifest_path.relative_to(root)), **attempt}
        row['local_directory'] = str(folder.relative_to(root))
        profile = folder / 'profile.json'
        if not profile.exists() or hashlib.sha256(profile.read_bytes()).hexdigest() != attempt['profile_sha256']:
            errors.append(f'{folder}: profile hash mismatch or missing snapshot')
        source_sha = attempt['source_sha256']
        source = manifest_path.parent / 'sources' / f'{source_sha}.tar.gz'
        if not source.exists():
            errors.append(f'{folder}: missing source snapshot {source_sha}')
        elif source not in checked_sources:
            digest = hashlib.sha256()
            with tarfile.open(source) as archive:
                for member in archive.getmembers():
                    if member.isfile():
                        digest.update(member.name.encode() + b'\0' + archive.extractfile(member).read())
            if digest.hexdigest() != source_sha:
                errors.append(f'{source}: source content hash mismatch')
            checked_sources.add(source)
        row['traces'] = []
        for trace in sorted(folder.glob('*.jsonl')):
            records = []
            for line in trace.read_text().splitlines():
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        errors.append(f'{trace}: incomplete JSON record')
            decisions = [r for r in records if r.get('type') == 'decision']
            if any(r.get('profile_sha256') != attempt['profile_sha256'] for r in decisions):
                errors.append(f'{trace}: decision/profile hash mismatch')
            summary = next((r for r in reversed(records) if r.get('type') == 'summary'), None)
            row['traces'].append({'path': str(trace.relative_to(root)),
                                  'sha256': hashlib.sha256(trace.read_bytes()).hexdigest(),
                                  'decisions': len(decisions), 'summary': summary})
        rows.append(row)
covered = {trace['path'] for row in rows for trace in row['traces']}
unmanifested = []
for path in sorted((root / 'runs/stages').rglob('*.jsonl')):
    if str(path.relative_to(root)) not in covered:
        records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        unmanifested.append({
            'path': str(path.relative_to(root)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'summary': next((r for r in reversed(records) if r.get('type') == 'summary'), None),
            'snapshot_coverage': 'No reservation manifest; do not infer an immutable source snapshot.',
        })
report = {'reservations': len(rows), 'source_archive_copies_checked': len(checked_sources),
          'unique_source_snapshots_checked': len({p.name for p in checked_sources}),
          'status_counts': dict(Counter(r['status'] for r in rows)),
          'errors': errors, 'attempts': rows, 'unmanifested_traces': unmanifested,
          'historical_exception': '1-1 B200 baseline has no immutable profile/source snapshot; see its result.json.'}
path = root / 'reports/stages/attempt-audit.json'
path.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'attempts'}))
if errors:
    raise SystemExit(1)
