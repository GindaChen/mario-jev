"""Publish an allowlisted, read-only view of the overnight Mario campaign."""
import argparse
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
import time

ROOT = Path(__file__).resolve().parent
SOURCE = Path(os.environ.get('MARIO_CAMPAIGN', '/home/juc049/projects/mario-amd/harness/runs/overnight-campaign'))
PUBLIC = ROOT / 'public/data'
STAGES = [f'{w}-{s}' for w in range(1, 9) for s in range(1, 5)]
MODES = {'continuous', 'continuous_with_recorded_restarts', 'stage_linked'}
STATUSES = {'running', 'needs_reflection', 'completed', 'error', 'paused', 'waiting_for_runner'}

def clean(value, limit=300):
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        return None
    text = str(value)
    text = re.sub(r'https?://\S+|/(?:home|Users|tmp)/\S+', '[private location]', text)
    text = re.sub(r'(?i)(?:api[_-]?key|authorization|access[_-]?token|secret)\s*[:=]\s*\S+', '[redacted]', text)
    return text[:limit]

def number(value, default=None):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) else default

def count(value):
    return max(0, int(number(value, 0)))

def stamp(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            return None
        return parsed.isoformat()
    except ValueError:
        return None

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def project(raw):
    """Never publish arbitrary config, endpoints, paths, artifacts, or error dumps."""
    if not isinstance(raw, dict):
        raise ValueError('Expected status object')
    results = raw.get('stage_results', {})
    results = results if isinstance(results, dict) else {}
    cleared = raw.get('cleared_stages', [])
    cleared = set(s for s in cleared if s in STAGES) if isinstance(cleared, list) else set()
    stages = {}
    for stage in STAGES:
        item = results.get(stage, {})
        item = item if isinstance(item, dict) else {}
        status = item.get('status', 'pending')
        if status == 'cleared':
            cleared.add(stage)
        if stage in cleared:
            status = 'cleared'
        stages[stage] = dict(status=status if status in {'pending', 'running', 'cleared'} else 'pending',
                             attempts=count(item.get('attempts')), retries=count(item.get('retries')),
                             checkpoint_retries=count(item.get('checkpoint_retries')),
                             completed_at=stamp(item.get('completed_at')))
    current = raw.get('current', {})
    current = current if isinstance(current, dict) else {}
    events = []
    for e in (raw.get('event_log') or [])[-100:]:
        if not isinstance(e, dict):
            continue
        events.append(dict(at=stamp(e.get('at')), kind=clean(e.get('kind'), 50),
                           stage=e.get('stage') if e.get('stage') in STAGES else None,
                           attempt=count(e.get('attempt')), message=clean(e.get('message'), 350)))
    totals = raw.get('counts', {})
    totals = totals if isinstance(totals, dict) else {}
    return dict(schema_version=1, campaign_id=clean(raw.get('campaign_id'), 100),
                status=raw.get('status') if raw.get('status') in STATUSES else 'waiting_for_runner',
                mode=raw.get('mode') if raw.get('mode') in MODES else 'unknown',
                started_at=stamp(raw.get('started_at')), updated_at=stamp(raw.get('updated_at')),
                current_stage=raw.get('current_stage') if raw.get('current_stage') in STAGES else None,
                current_attempt=count(raw.get('current_attempt')),
                stage_order=STAGES, cleared_stages=[s for s in STAGES if s in cleared], stage_results=stages,
                counts=dict(cleared=len(cleared), stages=32,
                            restarts=count(raw.get('restarts', totals.get('restarts'))),
                            checkpoint_retries=sum(s['checkpoint_retries'] for s in stages.values()),
                            total_decisions=count(raw.get('total_decisions', totals.get('total_decisions')))),
                current={k: (clean(current.get(k), 90) if k in {'action', 'room'} else number(current.get(k)))
                         for k in ['decision', 'x', 'room', 'latency_ms', 'action']}, event_log=events)

def final_artifacts(raw, data, public):
    """Only expose explicitly published final files backed by a matching audit."""
    if data.get('status') != 'completed' or data.get('counts', {}).get('cleared') != 32:
        return {}
    supplied = raw.get('artifacts', {}) if isinstance(raw, dict) else {}
    if not isinstance(supplied, dict):
        return {}
    files = {}
    for key, name in [('replay_url', 'campaign-replay.mp4'), ('verification_url', 'verification.json')]:
        url = supplied.get(key)
        if not isinstance(url, str) or not re.fullmatch(r'/data/campaign-final/[A-Za-z0-9_-]+/' + re.escape(name), url):
            return {}
        path = public / url.removeprefix('/data/')
        try:
            path.resolve().relative_to((public / 'campaign-final').resolve())
            if not path.is_file() or path.stat().st_size == 0:
                return {}
        except (ValueError, OSError):
            return {}
        files[key] = (url, path)
    if files['replay_url'][1].parent != files['verification_url'][1].parent:
        return {}
    try:
        audit_path = files['verification_url'][1]
        if audit_path.stat().st_size > 16_000_000:
            return {}
        audit = json.loads(audit_path.read_text())
        if not isinstance(audit, dict) or audit.get('campaign_id') != data.get('campaign_id') or audit.get('replay_verified') is not True or audit.get('completed') is not True:
            return {}
    except (ValueError, OSError):
        return {}
    replays = audit.get('replays', {})
    replays = replays if isinstance(replays, dict) else {}
    full = replays.get('full', {})
    if not isinstance(full, dict) or full.get('file') != 'campaign-replay.mp4' or full.get('kind') != 'chronological_attempts' or full.get('verified') is not True:
        return {}
    output = {key: pair[0] for key, pair in files.items()}
    for key, name, evidence, kind in [
        ('clears_url', 'campaign-clears.mp4', replays.get('clears', {}), 'stitched_stage_clears'),
        ('audit_url', 'campaign-audit.tar.gz', audit.get('audit_archive', {}), None),
    ]:
        if not isinstance(evidence, dict) or evidence.get('file') != name or evidence.get('verified') is not True or (kind and evidence.get('kind') != kind):
            continue
        url = supplied.get(key)
        expected = str(Path(files['replay_url'][0]).parent / name)
        if url != expected:
            continue
        path = public / url.removeprefix('/data/')
        try:
            path.resolve().relative_to(files['replay_url'][1].parent.resolve())
            if path.is_file() and path.stat().st_size > 0:
                output[key] = url
        except (ValueError, OSError):
            pass
    return output

def atomic(path, data):
    tmp = path.with_name(f'.{path.name}.{os.getpid()}.tmp')
    tmp.write_bytes(data)
    tmp.replace(path)

def publish(source=SOURCE, public=PUBLIC):
    public.mkdir(parents=True, exist_ok=True)
    status = source / 'status.json'
    error = None
    raw = {}
    try:
        if status.stat().st_size > 16_000_000:
            raise ValueError('Status too large')
        raw = json.loads(status.read_text())
        data = project(raw)
    except FileNotFoundError:
        data = project({})
    except (ValueError, TypeError, OSError):
        try:
            data = json.loads((public / 'campaign.json').read_text())
        except (ValueError, OSError):
            data = project({})
        error = 'Latest status could not be read; displaying the last published snapshot.'
    data.update(published_at=now(), feed_error=error, frame=None, artifacts=final_artifacts(raw, data, public))
    image = source / 'latest-frame.jpg'
    try:
        stat = image.stat()
        if 0 < stat.st_size < 10_000_000 and data.get('campaign_id'):
            dest = public / 'campaign-frame.jpg'
            if not dest.exists() or dest.stat().st_mtime_ns != stat.st_mtime_ns:
                content = image.read_bytes()
                if not content.startswith(b'\xff\xd8'):
                    raise ValueError('Not JPEG')
                atomic(dest, content)
                os.utime(dest, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            data['frame'] = dict(url='/data/campaign-frame.jpg', updated_at=dt.datetime.fromtimestamp(stat.st_mtime, dt.timezone.utc).isoformat())
    except (ValueError, OSError):
        pass
    atomic(public / 'campaign.json', (json.dumps(data, ensure_ascii=False, allow_nan=False) + '\n').encode())
    return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    while True:
        publish()
        if args.once:
            break
        time.sleep(2)
