"""Real runner subprocess with fake gameplay, including replica overlap detection."""
import json
import shutil
import subprocess
import sys
from pathlib import Path


def test_replica_pool_records_assignment_and_serializes_each_replica(tmp_path):
    repo = tmp_path / 'harness'
    (repo / 'scripts').mkdir(parents=True)
    (repo / '.venv/bin').mkdir(parents=True)
    source = Path(__file__).resolve().parents[1] / 'scripts/run_reflection_batch.py'
    runner = repo / 'scripts/run_reflection_batch.py'
    shutil.copy2(source, runner)
    fake = repo / '.venv/bin/mario-jev'
    fake.write_text(f'#!{sys.executable}\n' + '''import json, os, pathlib, sys, time
args = sys.argv[1:]
url = args[args.index('--djev-url') + 1]
folder = pathlib.Path(args[args.index('--log-dir') + 1])
lock = folder.parent / ('active-' + url.rsplit(':', 1)[-1])
try:
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
except FileExistsError:
    raise SystemExit(88)
os.close(fd)
try:
    (folder / 'observed.json').write_text(json.dumps({'url': url}))
    time.sleep(0.1)
finally:
    lock.unlink()
''')
    fake.chmod(0o755)
    profiles = []
    for index in range(4):
        profile = repo / f'p{index}.json'
        profile.write_text('{}')
        profiles.append(str(profile))
    endpoints = ['http://127.0.0.1:18515', 'http://127.0.0.1:18516']
    root = repo / 'runs'
    command = [sys.executable, str(runner), '--root', str(root), '--workers', '4',
               '--djev-urls', *endpoints, '--profiles', *profiles]
    subprocess.run(command, check=True, capture_output=True, timeout=15)
    attempts = json.loads((root / 'manifest.json').read_text())['attempts']
    assert len(attempts) == 4
    for index, attempt in enumerate(attempts):
        expected = endpoints[index % 2]
        assert attempt['djev_url'] == expected
        assert attempt['status'] == 'finished'  # Fake exits88 if replicas overlap.
        observed = json.loads((Path(attempt['directory']) / 'observed.json').read_text())
        assert observed['url'] == expected
        args = attempt['command']
        assert args[args.index('--djev-url') + 1] == expected
    # No pool retains the legacy endpoint and reservation accounting.
    subprocess.run([sys.executable, str(runner), '--root', str(root), '--workers', '1',
                    '--djev-url', endpoints[1], '--profiles', profiles[0]],
                   check=True, capture_output=True, timeout=15)
    attempts = json.loads((root / 'manifest.json').read_text())['attempts']
    assert len(attempts) == 5
    assert attempts[-1]['djev_url'] == endpoints[1]
    assert attempts[-1]['status'] == 'finished'
