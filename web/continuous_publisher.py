"""Publish allowlisted continuous-run status and frame snapshots; no model calls."""
import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path


def atomic(path, data):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_bytes(data)
    temp.replace(path)


def publish(root, public):
    config = json.loads((root / 'config.json').read_text())
    profile = (root / 'profiles/single.json').read_bytes()
    policy = json.loads(profile)
    status = json.loads((root / 'status.json').read_text()) if (root / 'status.json').exists() else {}
    attempts = [json.loads(p.read_text()) for p in sorted(root.glob('attempt-*/result.json'))]
    label = status.get('status', 'preparing')
    if attempts and attempts[-1]['outcome'] == 'completed':
        label = 'Completed: continuous 1-1 → 1-3 clear'
    elif len(attempts) >= config['attempts']:
        label = 'Batch finished: no continuous clear'
    current = {k: status[k] for k in ('attempt', 'stage', 'cleared', 'frames', 'decisions', 'current') if k in status}
    if not current and attempts:
        current = {k: attempts[-1][k] for k in ('attempt', 'furthest_stage', 'last_info')}
    frame = root / 'latest-frame.jpg'
    public.mkdir(parents=True, exist_ok=True)
    if frame.exists():
        atomic(public / 'frame.jpg', frame.read_bytes())
    data = {'updated_at': datetime.now(timezone.utc).isoformat(), 'status': label,
            'source_updated_at': datetime.fromtimestamp((root / 'status.json').stat().st_mtime, timezone.utc).isoformat() if (root / 'status.json').exists() else None,
            'attempt_limit': config['attempts'], 'current': current,
            'attempts': [{k: a[k] for k in ('attempt', 'outcome', 'cleared', 'furthest_stage', 'decisions', 'frames')} for a in attempts],
            'prompt': policy['instructions'], 'profile_sha256': hashlib.sha256(profile).hexdigest(),
            'has_frame': frame.exists()}
    atomic(public / 'policy.json', profile)
    atomic(public / 'status.json', (json.dumps(data, indent=2)+'\n').encode())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('public', type=Path)
    args = parser.parse_args()
    while True:
        try:
            publish(args.root, args.public)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        time.sleep(5)


if __name__ == '__main__':
    main()
