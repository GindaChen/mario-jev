"""Replay recorded CLM decisions without inference and verify full RAM and requests."""

import argparse
import hashlib
import json
from pathlib import Path

import httpx2

import mario_jev
from mario_jev.clm import ClmReflectionPolicy
from mario_jev.history import ObservationMemory
from mario_jev.policy import ACTIONS
from mario_jev.rsi_runtime.clm_pilot import make_env, profile
from mario_jev.rsi_runtime.clm_support import atomic, compact
from mario_jev.runner import execute_action


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(p):
    return json.loads(p.read_text())


def audit(root):
    root = Path(root)
    manifest = read(root / "manifest.json")
    attempts = []
    errors = []
    frames = 0
    decisions = 0
    try:
        assert (
            manifest["automatic_grounded_A_release"] and manifest["action_frames"] == 4
        )
        package = Path(mario_jev.__file__).parent
        for name, digest in manifest["source_sha256"].items():
            assert sha((root / "frozen/mario_jev" / name).read_bytes()) == digest
            assert sha((package / name).read_bytes()) == digest, (
                "runtime drift: " + name
            )
        for d in sorted((root / "attempts").iterdir()):
            if not (d / "summary.json").exists():
                continue
            s = read(d / "summary.json")
            v = s["program_version"]
            p = read(root / f"programs/v{v:04}/program.json")
            assert sha(compact(p).encode()) == s["program_sha256"]
            if manifest["protocol"] == "clm-single-prompt-v1":
                from mario_jev.rsi_runtime.clm_single_prompt import (
                    single_profile,
                    validate_single_program,
                )

                source = read(root / "frozen/source-program.json")
                validate_single_program(p, source["criteria"])
                expected_profile = single_profile(p, v)
            else:
                expected_profile = profile(p, v)
            assert read(root / f"programs/v{v:04}/profile.json") == expected_profile
            if v:
                provenance = read(root / f"programs/v{v:04}/provenance.json")
                assert provenance["review"]["allow"] is True
                assert read(root / provenance["proposal"])["program"] == p
            target = (manifest.get("world", 1), manifest.get("stage", 1))
            env = make_env(*target)
            policy = None
            current = {}

            def transport(request):
                assert json.loads(request.content) == current["request"], (  # noqa: B023 - synchronous callback uses current record
                    "CLM observation/prompt mismatch"
                )
                return httpx2.Response(200, json=current["response"])  # noqa: B023 - same synchronous record

            try:
                _, info = env.reset(seed=0)
                assert (int(info["world"]), int(info["stage"])) == target
                memory = ObservationMemory(12)
                assert (
                    sha(bytes(env.unwrapped.ram)) == manifest["checkpoint_ram_sha256"]
                )
                assert (
                    sha(Path(env.unwrapped._rom_path).read_bytes())
                    == manifest["rom_sha256"]
                )
                policy = ClmReflectionPolicy(
                    "http://replay.invalid",
                    root / f"programs/v{v:04}/profile.json",
                    transport=httpx2.MockTransport(transport),
                )
                count = 0
                maximum = 0
                release = 0
                terminal = False
                rows = sorted((d / "decisions").glob("*.json"))
                for index, path in enumerate(rows):
                    current = read(path)
                    assert not terminal and current["decision"] == index
                    assert (
                        current["source_frame"] == count
                        and current["program_sha256"] == s["program_sha256"]
                    )
                    state = memory.observe(env.unwrapped.ram, info, 4)
                    assert state == current["state"]
                    assert sha(bytes(env.unwrapped.ram)) == current["before_ram_sha256"]
                    assert (
                        sha((root / current["image"]).read_bytes())
                        == current["image_sha256"]
                    )
                    action, di = policy.choose(state)
                    assert (
                        action == current["action"]
                        and ACTIONS[action] == current["keys"]
                    )
                    assert (
                        di["decisions"]["selected_action"] == current["selected_action"]
                    )
                    assert di["decisions"]["rearm_release"] == current["rearm_release"]
                    assert di["requested_action_frames"] == current["requested_frames"]
                    info, reward, terminated, truncated, samples = execute_action(
                        env, action, current["requested_frames"]
                    )
                    assert (
                        samples == current["samples"]
                        and json.loads(compact(info)) == current["info"]
                    )
                    assert sha(bytes(env.unwrapped.ram)) == current["after_ram_sha256"]
                    transition = memory.finish(
                        state,
                        env.unwrapped.ram,
                        info,
                        action,
                        len(samples),
                        reward,
                        terminated,
                        samples,
                    )
                    assert transition == current["transition"]
                    count += len(samples)
                    frames += len(samples)
                    decisions += 1
                    release += current["rearm_release"]
                    assert count == current["result_frame"]
                    maximum = max(maximum, *(x["x"] for x in samples))
                    terminal = terminated or truncated or info["flag_get"]
                assert (
                    count == s["frames"]
                    and len(rows) == s["decisions"]
                    and maximum == s["max_x"]
                )
                assert release == s["automatic_releases"]
                assert (
                    bool(info["flag_get"])
                    == s["native_flag_get"]
                    == (s["outcome"] == "clear")
                )
                if s["outcome"] == "death":
                    assert info["is_dead"] or info["is_dying"]
                attempts.append(
                    {
                        k: s[k]
                        for k in (
                            "attempt_id",
                            "program_version",
                            "outcome",
                            "max_x",
                            "frames",
                            "automatic_releases",
                        )
                    }
                )
            finally:
                if policy:
                    policy.close()
                env.close()
    except Exception as exc:  # noqa: BLE001 - failed audits must return their error as evidence
        errors.append(repr(exc))
    return {
        "passed": not errors,
        "decisions_checked": decisions,
        "native_frames_checked": frames,
        "attempts": attempts,
        "errors": errors,
        "scope": "Completed attempts. Frozen sources, exact input requests, model replies, declared legacy controller aids, native RAM replay. Semantic compliance is reviewed separately.",
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    result = audit(a.root)
    if a.output:
        atomic(a.output, result)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
