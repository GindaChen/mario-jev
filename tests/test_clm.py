import copy
import json
from pathlib import Path

import httpx2
import pytest

from mario_jev.clm import ClmReflectionPolicy
from mario_jev.reflection import DEFAULT_CRITERIA


def test_clm_native_wire_and_legacy_rearm(tmp_path):
    p = tmp_path / "profile.json"
    p.write_text(
        json.dumps(
            {
                "name": "clm-test",
                "mode": "reflection",
                "one_frame_rearm": True,
                "instructions": "Play Mario.",
                "criteria": DEFAULT_CRITERIA,
                "memory_notes": [],
            }
        )
    )
    seen = []

    def handle(request):
        body = json.loads(request.content)
        seen.append(body)
        assert (
            set(body) == {"model", "state", "questions"}
            and body["model"] == "clm-latest"
        )
        assert "authorization" not in request.headers
        assert set(body["questions"]["action"]) == {"type", "instructions", "criteria"}
        return httpx2.Response(
            200,
            json={
                "model": "clm-latest",
                "answers": {
                    "action": {
                        "type": "choice",
                        "choice": "right_run_jump",
                        "confidence": 1,
                        "probabilities": {
                            k: float(k == "right_run_jump") for k in DEFAULT_CRITERIA
                        },
                    }
                },
                "usage": {"input_tokens": 100, "output_tokens": 0, "billing_units": 1},
            },
        )

    policy = ClmReflectionPolicy(
        "http://local", p, transport=httpx2.MockTransport(handle)
    )
    s = json.loads((Path(__file__).parent / "fixtures/laya_wall.json").read_text())
    s["mario"].update(grounded=True, feet_y=144)
    s["action_frames"] = 4
    s["jump_already_held"] = False
    try:
        action, d = policy.choose(s)
        assert action == "right_run_jump" and not d["decisions"]["rearm_release"]
        t = copy.deepcopy(s)
        t["jump_already_held"] = True
        action, d = policy.choose(t)
        assert action == "right_run" and d["requested_action_frames"] == 1
        assert d["backend"] == "clm" and d["actual_request"] == seen[-1]
        assert d["actual_response"]["model"] == "clm-latest"
        assert d["decisions"]["selected_action"] == "right_run_jump"
    finally:
        policy.close()


def test_reflection_cannot_add_router_or_change_action_set():
    from mario_jev.rsi_runtime.clm_pilot import profile, validate_program

    p = {
        "instructions": "Play Mario.",
        "criteria": dict(DEFAULT_CRITERIA),
        "memory": "Release during descent.",
    }
    assert profile(p, 1)["memory_notes"] == [
        {"id": "learned", "instructions": p["memory"]}
    ]
    with pytest.raises(ValueError):
        validate_program({**p, "action_frames": 100})
    with pytest.raises(ValueError):
        validate_program({**p, "memory_notes": [{"min_x": 500}]})
    with pytest.raises(ValueError):
        validate_program({**p, "criteria": {"right_run": "Run right."}})


def test_continuation_preserves_attempt_budget_and_empty_initial_memory(tmp_path):
    from types import SimpleNamespace

    from mario_jev.rsi_runtime.clm_pilot import ClmPilot
    from mario_jev.rsi_runtime.clm_support import atomic

    control = tmp_path / "control"
    (control / "template").mkdir(parents=True)
    (control / "template/initial-instructions.md").write_text("Play Mario.")
    (control / "model-revisions.json").write_text("{}")
    args = SimpleNamespace(
        control=control,
        name="parent",
        resume_from=None,
        wall_limit=10800,
        max_attempts=50,
        endpoint="http://unused",
    )
    parent = ClmPilot(args)
    parent.attempt = 1
    summary = {
        "attempt_id": 1,
        "program_version": 0,
        "outcome": "stalled",
        "frames": 454,
        "max_x": 40,
    }
    (parent.root / "attempts/0001").mkdir()
    atomic(parent.root / "attempts/0001/summary.json", summary)
    parent.status["status"] = "infra_error"
    parent.save_status()
    parent.manifest.update(checkpoint_ram_sha256="checkpoint", rom_sha256="rom")
    atomic(parent.root / "manifest.json", parent.manifest)
    args.name = "child"
    args.resume_from = parent.root
    child = ClmPilot(args)
    assert child.next_attempt == 2 and child.pending_reflection
    assert child.total_frames == 454 and child.program["memory"] == ""
    assert (
        child.manifest["max_attempts"] == 50
        and child.manifest["created_unix"] == parent.manifest["created_unix"]
    )
    assert child.manifest["checkpoint_ram_sha256"] == "checkpoint"


def test_fixed_ablation_keeps_prompt_after_failure_without_s2(tmp_path):
    from types import SimpleNamespace

    from mario_jev.rsi_runtime.clm_fixed import FixedNoMemoryPilot

    control = tmp_path / "control"
    (control / "template").mkdir(parents=True)
    (control / "template/initial-instructions.md").write_text("Play Mario.")
    (control / "model-revisions.json").write_text("{}")
    source = {
        "instructions": "Reach the flag.",
        "criteria": dict(DEFAULT_CRITERIA),
        "memory": "A previous failure note.",
    }
    source_path = tmp_path / "source.json"
    source_path.write_text(json.dumps(source))
    args = SimpleNamespace(
        control=control,
        name="fixed",
        source_program=source_path,
        resume_from=None,
        wall_limit=60,
        max_attempts=3,
        endpoint="http://unused",
    )
    pilot = FixedNoMemoryPilot(args)
    assert pilot.program == {**source, "memory": ""}
    profile = json.loads((pilot.root / "programs/v0000/profile.json").read_text())
    assert profile["memory_notes"] == []

    def failed_attempt():
        summary = {
            "attempt_id": pilot.attempt,
            "outcome": "death",
            "native_flag_get": False,
        }
        pilot.summaries.append(summary)
        return summary, []

    pilot.attempt_run = failed_attempt
    pilot.run()
    assert len(pilot.summaries) == 3 and pilot.version == 0
    assert (
        not list((pilot.root / "reflections").iterdir()) and not pilot.container_names
    )
    assert len(list((pilot.root / "programs").iterdir())) == 1
    assert pilot.manifest["reflection_enabled"] is False
    with pytest.raises(RuntimeError):
        pilot.codex("must not run")
    with pytest.raises(RuntimeError):
        pilot.publish()


def test_single_prompt_preserves_merged_text_but_removes_note_clock(tmp_path):
    from mario_jev.rsi_runtime.clm_pilot import profile
    from mario_jev.rsi_runtime.clm_single_prompt import single_profile

    source = {
        "instructions": "Play Mario.",
        "criteria": dict(DEFAULT_CRITERIA),
        "memory": "Use current geometry.",
    }
    program = {
        "instructions": source["instructions"] + "\n" + source["memory"],
        "criteria": source["criteria"],
    }
    old = tmp_path / "old.json"
    old.write_text(json.dumps(profile(source, 0)))
    new = tmp_path / "new.json"
    new.write_text(json.dumps(single_profile(program, 0)))
    seen = []

    def handle(request):
        seen.append(json.loads(request.content))
        return httpx2.Response(
            200,
            json={
                "model": "clm-latest",
                "answers": {
                    "action": {
                        "type": "choice",
                        "choice": "right_jump",
                        "confidence": 1,
                        "probabilities": {
                            k: float(k == "right_jump") for k in DEFAULT_CRITERIA
                        },
                    }
                },
                "usage": {"input_tokens": 100, "output_tokens": 0, "billing_units": 1},
            },
        )

    state = json.loads((Path(__file__).parent / "fixtures/laya_wall.json").read_text())
    state["mario"].update(grounded=True, feet_y=144)
    state["action_frames"] = 4
    state["jump_already_held"] = True
    outputs = []
    for path in (old, new):
        policy = ClmReflectionPolicy(
            "http://local", path, transport=httpx2.MockTransport(handle)
        )
        try:
            outputs.append(policy.choose(copy.deepcopy(state)))
        finally:
            policy.close()
    assert seen[0]["state"].pop("note_elapsed_frames") == {"learned": 0}
    assert seen[0] == seen[1]
    assert seen[1]["questions"]["action"]["instructions"] == program["instructions"]
    assert outputs[0][0] == outputs[1][0] == "right"
    assert outputs[1][1]["decisions"]["rearm_release"]
    assert outputs[1][1]["active_memory_notes"] == []


def test_single_prompt_reflection_can_only_rewrite_instructions(tmp_path):
    from types import SimpleNamespace

    from mario_jev.rsi_runtime.clm_single_prompt import SinglePromptPilot

    control = tmp_path / "control"
    (control / "template").mkdir(parents=True)
    (control / "template/initial-instructions.md").write_text("Unused legacy default.")
    (control / "template/system2-instructions.md").write_text(
        "Only rewrite instructions; no memory."
    )
    (control / "model-revisions.json").write_text("{}")
    source = {
        "instructions": "Reach the flag.",
        "criteria": dict(DEFAULT_CRITERIA),
        "memory": "A useful lesson.",
    }
    source_path = tmp_path / "source.json"
    source_path.write_text(json.dumps(source))
    args = SimpleNamespace(
        control=control,
        name="single",
        source_program=source_path,
        resume_from=None,
        wall_limit=60,
        max_attempts=3,
        endpoint="http://unused",
        fixed=False,
    )
    pilot = SinglePromptPilot(args)
    pilot.attempt = 1
    assert pilot.program["instructions"] == "Reach the flag.\nA useful lesson."
    assert set(pilot.program) == {"instructions", "criteria"}
    with pytest.raises(ValueError):
        pilot.validate_candidate({**pilot.program, "memory": ""})
    with pytest.raises(ValueError):
        pilot.validate_candidate({**pilot.program, "memory_notes": []})
    changed = {
        **pilot.program,
        "criteria": {**pilot.program["criteria"], "right": "New candidate"},
    }
    with pytest.raises(ValueError):
        pilot.validate_candidate(changed)
    summary = {"attempt_id": 1, "outcome": "death", "max_x": 100, "program_version": 0}
    pilot.summaries.append(summary)
    row = {
        "decision": 0,
        "source_frame": 0,
        "request": {"state": {}},
        "selected_action": "right",
        "action": "right",
        "rearm_release": False,
        "response": {"answers": {"action": {"probabilities": {}}}},
        "transition": {"after": {}},
        "image": "attempts/0001/images/00000.jpg",
    }
    calls = []

    def fake_codex(prompt, folder, reviewer=False, images=()):
        calls.append((prompt, reviewer))
        if reviewer:
            return {"allow": True, "reason": "Only the single prompt changed."}
        return {
            "attempt_id": 1,
            "base_version": 0,
            "hypothesis": "Respond earlier to approaching enemies.",
            "evidence": [0],
            "prediction": "Choose a moving jump before contact.",
            "program": {
                **pilot.program,
                "instructions": "Jump before contacting visible enemies.",
            },
        }

    pilot.codex = fake_codex
    pilot.reflect_checked(summary, [row])
    assert pilot.version == 1 and len(calls) == 2 and calls[1][1]
    assert "Only the single instructions string may change" in calls[1][0]
    saved = json.loads((pilot.root / "programs/v0001/profile.json").read_text())
    assert "memory_notes" not in saved and saved["single_prompt"]
    assert saved["criteria"] == source["criteria"]
    assert (pilot.root / "programs/v0001/instructions.md").read_text() == pilot.program[
        "instructions"
    ]
    args.name = "fixed"
    args.fixed = True
    fixed = SinglePromptPilot(args)
    with pytest.raises(RuntimeError):
        fixed.codex("forbidden")
    with pytest.raises(RuntimeError):
        fixed.publish()


def test_single_prompt_never_overrides_model_choice_at_old_stage_boundaries(
    tmp_path, monkeypatch
):
    """Old lesson-region boundaries must not force a movement or jump."""
    from mario_jev.djev import ModularDjevPolicy
    from mario_jev.reflection import ReflectionDjevPolicy
    from mario_jev.rsi_runtime.clm_single_prompt import single_profile

    def forbidden(*args, **kwargs):
        raise AssertionError("Legacy routing/fallback must not run")

    monkeypatch.setattr(ReflectionDjevPolicy, "_activation_matches", forbidden)
    monkeypatch.setattr(ModularDjevPolicy, "choose", forbidden)
    p = tmp_path / "profile.json"
    prompt = "Play 1-2. The model decides whether a lesson applies."
    p.write_text(
        json.dumps(
            single_profile(
                {"instructions": prompt, "criteria": dict(DEFAULT_CRITERIA)}, 0
            )
        )
    )
    fixture = json.loads(
        (Path(__file__).parent / "fixtures/laya_wall.json").read_text()
    )
    calls = []
    for choice in DEFAULT_CRITERIA:

        def handle(request, selected=choice):
            body = json.loads(request.content)
            calls.append(body)
            return httpx2.Response(
                200,
                json={
                    "model": "clm-latest",
                    "answers": {
                        "action": {
                            "type": "choice",
                            "choice": selected,
                            "confidence": 1,
                            "probabilities": {
                                k: float(k == selected) for k in DEFAULT_CRITERIA
                            },
                        }
                    },
                    "usage": {
                        "input_tokens": 100,
                        "output_tokens": 0,
                        "billing_units": 1,
                    },
                },
            )

        policy = ClmReflectionPolicy(
            "http://local", p, transport=httpx2.MockTransport(handle)
        )
        try:
            for x in (
                0,
                939,
                940,
                1020,
                1021,
                1259,
                1260,
                1325,
                1390,
                1490,
                1491,
                3161,
            ):
                state = copy.deepcopy(fixture)
                state["mario"].update(x=x, grounded=True, feet_y=144)
                state["action_frames"] = 4
                state["jump_already_held"] = False
                action, di = policy.choose(state)
                assert action == choice and not di["decisions"]["rearm_release"]
                assert di["active_memory_notes"] == []
                assert set(calls[-1]["questions"]) == {"action"}
                assert calls[-1]["questions"]["action"]["instructions"] == prompt
                assert calls[-1]["questions"]["action"]["criteria"] == DEFAULT_CRITERIA
                assert "note_elapsed_frames" not in calls[-1]["state"]
        finally:
            policy.close()
    assert len(calls) == len(DEFAULT_CRITERIA) * 12


def test_single_prompt_rejects_legacy_geographic_configuration(tmp_path):
    from mario_jev.rsi_runtime.clm_single_prompt import single_profile

    base = single_profile(
        {"instructions": "Play Mario.", "criteria": dict(DEFAULT_CRITERIA)}, 0
    )
    for key, value in {
        "memory_notes": [],
        "reflection_start_x": 940,
        "instruction_router": {},
        "thresholds": {},
        "observation_style": "facts",
    }.items():
        p = tmp_path / "bad.json"
        p.write_text(json.dumps({**base, key: value}))
        with pytest.raises(ValueError, match="notes or routers"):
            ClmReflectionPolicy("http://unused", p)


def test_fixed_environment_selects_stage_only_at_reset():
    from mario_jev.rsi_runtime.clm_support import FixedFrameFactory

    for stage in (1, 2):
        env = FixedFrameFactory.make(world=1, stage=stage)
        try:
            _, info = env.reset(seed=0)
            assert (info["world"], info["stage"]) == (1, stage)
            assert env.is_single_stage_env
        finally:
            env.close()
    with pytest.raises(ValueError):
        FixedFrameFactory.make(world=1, stage=5)
