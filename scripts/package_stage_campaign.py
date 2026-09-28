#!/usr/bin/env python3
"""Package the stage audit without modifying any original run dataset."""
import hashlib
import json
import tarfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
output = root / 'deliverables/stage-campaign-audit.tar.gz'
manifest_path = root / 'deliverables/stage-campaign-audit-manifest.json'
files = set()
for folder in ('runs/stages', 'runs/djev-reflection-100', 'prompts/stages',
               'prompts/reflection', 'reports/reflection', 'reports/stages',
               'deliverables/stages', 'src', 'tests', 'scripts', 'serving'):
    for path in (root / folder).rglob('*'):
        if (path.is_file() and '__pycache__' not in path.parts and
                path.name != '.DS_Store' and not path.name.endswith(('.zip', '.pyc')) and
                (not path.name.endswith('.tar.gz') or 'sources' in path.parts)):
            files.add(path)
for name in ('README.md', 'pyproject.toml', 'uv.lock', 'requirements.txt',
             'deliverables/stage-campaign-index.md'):
    path = root / name
    if path.is_file():
        files.add(path)
for result in (root / 'deliverables/stages').glob('*/result.json'):
    trace_name = json.loads(result.read_text()).get('trace')
    if not trace_name:
        continue
    trace = root / trace_name
    if trace.is_file():
        files.add(trace)
entries = []
for path in sorted(files):
    data = path.read_bytes()
    entries.append({'path': str(path.relative_to(root)), 'bytes': len(data),
                    'sha256': hashlib.sha256(data).hexdigest()})
manifest = {
    'description': 'Original trajectories, prompts, source snapshots, reflection reports and winner replays.',
    'stages': json.loads((root / 'reports/stages/status.json').read_text()),
    'files': entries,
}
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
with tarfile.open(output, 'w:gz', compresslevel=6) as archive:
    for path in sorted(files | {manifest_path}):
        archive.add(path, arcname=str(path.relative_to(root)), recursive=False)
print(json.dumps({'archive': str(output), 'bytes': output.stat().st_size,
                  'files': len(entries), 'manifest': str(manifest_path)}))
