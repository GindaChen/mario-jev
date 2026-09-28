"""Bounded CPU-only rendering of published, finished attempts; no inference calls."""
import concurrent.futures
import json
import os
from pathlib import Path
import re
import subprocess
import threading

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / 'public'
HARNESS = Path(os.environ.get('MARIO_HARNESS', '/home/juc049/projects/mario-amd/harness'))
ID = re.compile(r'\d{8}T\d{12}Z')


class ReplayService:
    def __init__(self, public=PUBLIC, harness=HARNESS, renderer=None):
        self.public, self.harness = Path(public), Path(harness)
        self.renderer = renderer or self.render
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.jobs = {}
        self.lock = threading.Lock()

    def request(self, rid):
        if not ID.fullmatch(rid):
            return 404, {'status': 'unavailable', 'message': 'Unknown attempt.'}
        try:
            detail = json.loads((self.public / 'data/runs' / f'{rid}.json').read_text())
        except (OSError, ValueError):
            return 404, {'status': 'unavailable', 'message': 'Unknown attempt.'}
        if not detail.get('finished'):
            return 200, {'status': 'recording', 'message': 'This attempt is still recording. Replay will be available when it finishes.'}
        if not detail.get('decisions'):
            return 200, {'status': 'unavailable', 'message': 'This attempt contains no recorded gameplay.'}
        out = self.public / 'media/attempts' / f'{rid}.mp4'
        if out.is_file():
            return 200, {'status': 'ready', 'video': f'/media/attempts/{rid}.mp4'}
        with self.lock:
            job = self.jobs.get(rid)
            if job:
                if not job.done():
                    return 202, {'status': 'preparing', 'message': 'Preparing this attempt’s replay…'}
                if job.exception():
                    return 200, {'status': 'error', 'message': 'This recording could not be replayed exactly. The run evidence remains available.'}
            if sum(not j.done() for j in self.jobs.values()) >= 8:
                return 503, {'status': 'busy', 'message': 'Replay preparation is busy. Retrying shortly…'}
            # A public run ID is the only input. Never accept a path from the browser.
            traces = list((self.harness / 'runs').glob(f'**/{rid}.jsonl'))
            if len(traces) != 1 or not traces[0].resolve().is_relative_to((self.harness / 'runs').resolve()):
                return 404, {'status': 'unavailable', 'message': 'The source recording is unavailable.'}
            out.parent.mkdir(parents=True, exist_ok=True)
            self.jobs[rid] = self.pool.submit(self.renderer, traces[0], out)
            # Retain pending jobs and only a bounded set of completed errors.
            for old in list(self.jobs):
                if len(self.jobs) <= 64:
                    break
                if self.jobs[old].done() and old != rid:
                    del self.jobs[old]
        return 202, {'status': 'preparing', 'message': 'Preparing this attempt’s replay…'}

    def render(self, trace, out):
        temporary = out.with_name(out.stem + '.building.mp4')
        temporary.unlink(missing_ok=True)
        command = [str(self.harness / '.venv/bin/python'), str(self.harness / 'scripts/export_replay.py'), str(trace), str(temporary)]
        # Linux subprocess and ffmpeg inherit one CPU affinity; the web process
        # and experiment workers retain their existing affinity/settings.
        if hasattr(os, 'sched_getaffinity'):
            command = ['taskset', '-c', str(min(os.sched_getaffinity(0))), 'nice', '-n', '10', *command]
        environment = {**os.environ, 'PATH': str(ROOT / 'bin') + os.pathsep + os.environ.get('PATH', ''), 'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'}
        try:
            result = subprocess.run(command, cwd=self.harness, env=environment,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
            if result.returncode or not temporary.is_file():
                raise RuntimeError('Replay verification or encoding failed')
            temporary.replace(out)
        finally:
            temporary.unlink(missing_ok=True)
