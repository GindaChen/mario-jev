#!/usr/bin/env python3
"""Run a bounded, reproducible batch of fresh AMD-local DJev experiments."""

import argparse
import concurrent.futures
import fcntl
import hashlib
import json
import os
import re
import signal
import subprocess
import tarfile
import threading
from datetime import UTC, datetime
from pathlib import Path


def now():
    return datetime.now(UTC).isoformat()


def save(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def source_snapshot(repo, root):
    files = sorted(
        p
        for folder in ("src", "scripts")
        for p in (repo / folder).rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix in (".py", ".sh")
    )
    files += [
        p for name in ("pyproject.toml", "uv.lock") if (p := repo / name).exists()
    ]
    digest = hashlib.sha256()
    for path in files:
        digest.update(str(path.relative_to(repo)).encode() + b"\0" + path.read_bytes())
    sha = digest.hexdigest()
    destination = root / "sources" / (sha + ".tar.gz")
    destination.parent.mkdir(exist_ok=True)
    if not destination.exists():
        with tarfile.open(destination, "w:gz") as archive:
            for path in files:
                archive.add(path, arcname=str(path.relative_to(repo)))
    return sha, str(destination)


def reserve(manifest, profiles, repeats, root, source_sha, frames, max_attempts=100):
    """Reservations count conservatively, including errors and interrupted launches."""
    attempts = manifest.setdefault("attempts", [])
    count = len(profiles) * repeats
    if len(attempts) + count > max_attempts:
        raise ValueError(
            f"{max_attempts}-attempt cap: {len(attempts)} reserved; requested {count}"
        )
    batch = []
    for _ in range(repeats):
        for profile in profiles:
            number = len(attempts) + 1
            name = re.sub(r"[^a-zA-Z0-9_-]", "_", profile.stem)
            directory = root / f"{number:03d}-{name}"
            directory.mkdir(exist_ok=False)
            data = profile.read_bytes()
            snapshot = directory / "profile.json"
            snapshot.write_bytes(data)
            snapshot.chmod(0o444)
            attempt = {
                "id": number,
                "profile": str(profile),
                "profile_snapshot": str(snapshot),
                "profile_sha256": hashlib.sha256(data).hexdigest(),
                "source_sha256": source_sha,
                "directory": str(directory),
                "status": "reserved",
                "reserved_at": now(),
                "frames": frames,
            }
            attempts.append(attempt)
            batch.append(attempt)
    return batch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("runs/djev-reflection-100"))
    parser.add_argument("--profiles", type=Path, nargs="+", required=True)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--max-attempts", type=int, default=100,
                        help="Total reservations allowed in this campaign root")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--frames", type=int, default=4)
    parser.add_argument("--djev-url", default="http://127.0.0.1:18515", help="AMD-local DJev replica endpoint")
    parser.add_argument("--djev-urls", nargs="+", help="Optional replica pool: assign trials round-robin, at most one trial per endpoint")
    parser.add_argument("--world", type=int, choices=range(1, 9), default=1)
    parser.add_argument("--stage", type=int, choices=range(1, 5), default=2)
    parser.add_argument("--stall-decisions", type=int, default=120)
    args = parser.parse_args()
    if min(args.repeats, args.workers, args.frames, args.stall_decisions, args.max_attempts) < 1:
        parser.error("repeats, workers, and frames must be positive")
    if args.djev_urls and len(set(args.djev_urls)) != len(args.djev_urls):
        parser.error("--djev-urls must contain unique endpoints")
    repo = Path(__file__).resolve().parents[1]
    root = args.root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    profiles = [p.resolve() for p in args.profiles]
    for profile in profiles:
        json.loads(profile.read_text())
    with (root / ".runner.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.exit(
                2, "Another runner or its game processes still hold this root lock.\n"
            )
        manifest_path = root / "manifest.json"
        manifest = (
            json.loads(manifest_path.read_text())
            if manifest_path.exists()
            else {"version": 1, "budget": 100, "created_at": now(), "attempts": []}
        )
        target = {"world": args.world, "stage": args.stage}
        if manifest.get("target", {"world": 1, "stage": 2}) != target and manifest["attempts"]:
            parser.error("Use a separate root for each stage")
        manifest["target"] = target
        # The lock is inherited by children, so an unlocked root cannot have our old games running.
        for attempt in manifest["attempts"]:
            if attempt["status"] in ("reserved", "running"):
                attempt.update(status="interrupted", ended_at=now())
        sha, snapshot = source_snapshot(repo, root)
        manifest.setdefault("sources", {})[sha] = snapshot
        try:
            batch = reserve(manifest, profiles, args.repeats, root, sha, args.frames,
                            args.max_attempts)
        except ValueError as error:
            parser.exit(2, str(error) + "\n")
        for index, attempt in enumerate(batch):
            attempt["djev_url"] = (
                args.djev_urls[index % len(args.djev_urls)]
                if args.djev_urls else args.djev_url
            )
        save(
            manifest_path, manifest
        )  # Persist the entire allocation before any process starts.
        mutex = threading.Lock()
        stopping = threading.Event()
        processes = set()
        endpoint_locks = {url: threading.Lock() for url in args.djev_urls or []}

        def stop(signum, frame):
            stopping.set()
            with mutex:
                for process in tuple(processes):
                    process.terminate()

        signal.signal(signal.SIGINT, stop)
        signal.signal(signal.SIGTERM, stop)

        def run_on_endpoint(attempt):
            directory = Path(attempt["directory"])
            command = [
                str(repo / ".venv/bin/mario-jev"),
                "--policy",
                "djev",
                "--djev-url",
                attempt["djev_url"],
                "--djev-api-path",
                "/v1/systemone",
                "--djev-profile",
                attempt["profile_snapshot"],
                "--world",
                str(args.world),
                "--stage",
                str(args.stage),
                "--stall-decisions",
                str(args.stall_decisions),
                "--headless",
                "--decisions",
                "2000",
                "--log-every",
                "100",
                "--frames",
                str(args.frames),
                "--log-dir",
                str(directory),
            ]
            try:
                with (directory / "stdout.log").open("w") as output:
                    with mutex:
                        if stopping.is_set():
                            attempt.update(status="cancelled", ended_at=now())
                            save(manifest_path, manifest)
                            return
                        attempt.update(
                            status="running", started_at=now(), command=command
                        )
                        save(manifest_path, manifest)
                        process = subprocess.Popen(
                            command,
                            cwd=repo,
                            stdout=output,
                            stderr=subprocess.STDOUT,
                            env={**os.environ, "PYTHONUNBUFFERED": "1"},
                            pass_fds=(lock.fileno(),),
                        )
                        processes.add(process)
                        attempt["pid"] = process.pid
                        save(manifest_path, manifest)
                    code = process.wait()
                    with mutex:
                        processes.discard(process)
                        attempt.update(
                            status="finished" if code == 0 else "error",
                            returncode=code,
                            ended_at=now(),
                        )
                        save(manifest_path, manifest)
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                with mutex:
                    attempt.update(status="error", error=str(error), ended_at=now())
                    save(manifest_path, manifest)
            print(
                json.dumps(
                    {
                        key: attempt.get(key)
                        for key in ("id", "status", "returncode", "directory")
                    }
                ),
                flush=True,
            )

        def run(attempt):
            # Pool mode keeps each trial on one replica and prevents batch overlap
            # there. Legacy single-URL mode still permits concurrent trials.
            endpoint_lock = endpoint_locks.get(attempt["djev_url"])
            if endpoint_lock is None:
                run_on_endpoint(attempt)
            else:
                with endpoint_lock:
                    run_on_endpoint(attempt)

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            list(pool.map(run, batch))
        if stopping.is_set():
            raise SystemExit(130)


if __name__ == "__main__":
    main()
