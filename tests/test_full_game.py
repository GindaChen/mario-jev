import numpy as np

from mario_jev.full_game import STAGES, RunProgress, make_full_game
from mario_jev.policy import ACTIONS


def info(stage="1-1", **kwargs):
    world, level = map(int, stage.split("-"))
    return dict(
        world=world,
        stage=level,
        player_state=8,
        is_world_over=False,
        is_dead=False,
        is_dying=False,
        is_game_over=False,
        life=2,
        **kwargs,
    )


def test_native_steps_match_raw_emulator_and_keep_initial_timer():
    env, initial = make_full_game()
    reference, _ = make_full_game()
    try:
        assert initial["time"] == 400
        assert len(env.unwrapped.boot_actions) > 100
        for index in range(240):
            action = "right_run_jump" if index % 64 < 32 else "right_run"
            env.step(list(ACTIONS).index(action))
            reference.unwrapped._env.frame_advance(
                reference._action_map[list(ACTIONS).index(action)]
            )
            np.testing.assert_array_equal(env.unwrapped.ram, reference.unwrapped.ram)
            np.testing.assert_array_equal(
                env.unwrapped.screen, reference.unwrapped.screen
            )
    finally:
        env.close()
        reference.close()


def test_death_is_not_a_stage_clear_and_reset_restores_full_game():
    env, before = make_full_game()
    progress = RunProgress()
    try:
        for _ in range(1000):
            _, _, _, _, after = env.step(list(ACTIONS).index("right_run"))
            outcome = progress.observe(before, after)
            if outcome:
                break
            before = after
        assert outcome == "death"
        assert progress.cleared == []
        _, reset = env.reset(seed=123)
        assert (reset["world"], reset["stage"], reset["time"], reset["life"]) == (
            1,
            1,
            400,
            2,
        )
    finally:
        env.close()


def test_only_ordered_playable_transitions_credit_this_attempt():
    progress = RunProgress()
    before = info()
    intermediate = info("1-3")
    intermediate["player_state"] = 7
    assert progress.observe(before, intermediate) is None
    assert progress.cleared == []
    assert progress.observe(intermediate, info("1-3")) == "unexpected_stage_transition"
    for stage in STAGES[1:]:
        after = info(stage)
        assert progress.observe(before, after) is None
        before = after
    final = info("8-4")
    final["is_world_over"] = True
    assert progress.observe(before, final) == "completed"
    assert progress.cleared == STAGES
    assert RunProgress().cleared == []


def test_extra_life_does_not_end_attempt_but_death_during_transition_does():
    progress = RunProgress()
    before, after = info(), info("1-2")
    after["life"] = 3
    assert progress.observe(before, after) is None
    dead = info("1-3")
    dead["is_dying"] = True
    assert progress.observe(after, dead) == "death"
    assert progress.cleared == ["1-1"]


def test_runner_death_restarts_and_replay_checks_ram(tmp_path, monkeypatch):
    import importlib
    import json
    from pathlib import Path
    from types import SimpleNamespace

    import pytest

    monkeypatch.syspath_prepend(str(Path(__file__).parents[1] / "scripts"))
    runner = importlib.import_module("run_full_game")

    class WalkPolicy:
        def __init__(self, *args, **kwargs):
            pass

        def choose(self, state):
            return "right_run", {"control_origin": "test_policy"}

        def close(self):
            pass

    monkeypatch.setattr(runner, "DjevPolicy", WalkPolicy)
    profiles = runner.freeze_profiles(tmp_path, None)
    args = SimpleNamespace(
        seed=123, endpoint="unused", max_frames=2000, max_decisions=500
    )
    for number in (1, 2):
        result = runner.attempt(tmp_path, number, args, profiles)
        assert result["outcome"] == "death"
        assert result["cleared"] == []
        trace = tmp_path / f"attempt-{number:03d}" / "trajectory.jsonl"
        assert runner.replay(trace)["verified"]
        reset = json.loads(trace.read_text().splitlines()[0])
        assert reset["result"]["info"]["time"] == 400
        assert reset["result"]["info"]["stage"] == 1
    rows = [json.loads(line) for line in trace.read_text().splitlines()]
    step = next(row for row in rows if row["type"] == "step")
    step["result"]["ram_sha256"] = "tampered"
    trace.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    with pytest.raises(AssertionError, match="Replay mismatch"):
        runner.replay(trace)
