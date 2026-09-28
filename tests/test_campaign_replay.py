import importlib.util
import io
import json
import sys
from pathlib import Path

import numpy as np
import pytest

scripts = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(scripts))
try:
    spec = importlib.util.spec_from_file_location(
        "campaign_replay", scripts / "replay_campaign.py"
    )
    replay = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(replay)
finally:
    sys.path.remove(str(scripts))


def trace_file(tmp_path, rows):
    path = tmp_path / "trajectory.jsonl"
    path.write_text(
        "".join(
            json.dumps(dict(sequence=i, **row)) + "\n" for i, row in enumerate(rows)
        )
    )
    return path


def event(kind, stage="1-1", attempt=1):
    return {"type": "event", "kind": kind, "stage": stage, "attempt": attempt}


def reset(stage="1-1"):
    return {
        "type": "reset",
        "env": f"SuperMarioBros-{stage}-v0",
        "stage": stage,
        "seed": 123,
        "reason": "explicit_stage_loader",
    }


def test_distinguishes_natural_transitions_new_loads_retries_and_partial_loads(
    tmp_path,
):
    path = trace_file(
        tmp_path,
        [
            reset(),
            event("stage_start"),
            event("stage_clear"),
            event("stage_start", "1-2"),
            event("stage_failure", "1-2"),
            reset("1-2"),
            event("stage_start", "1-2", 2),
            event("stage_clear", "1-2", 2),
            reset("1-3"),
            event("stage_start", "1-3"),
            event("stage_failure", "1-3"),
            reset("1-3"),
        ],
    )
    loads, winners, natural = replay.index_trace(path)
    assert [r["kind"] for r in loads.values()] == [
        "stage_load",
        "retry",
        "stage_load",
        "unclassified",
    ]
    assert winners == {"1-1": 1, "1-2": 2}
    assert natural == 1


def test_resumed_attempt_is_retry_even_without_earlier_attempt_in_file(tmp_path):
    path = trace_file(tmp_path, [reset("3-2"), event("stage_start", "3-2", 4)])
    loads, _, _ = replay.index_trace(path)
    assert loads[0]["kind"] == "retry"


def decision(attempt, cleared=False, x=1):
    return {
        "type": "decision",
        "stage": "1-1",
        "attempt": attempt,
        "action": "right_run",
        "frames_executed": 1,
        "result": {
            "x": x,
            "y": 176,
            "world": 1,
            "stage": 1,
            "flag_get": cleared,
            "terminated": True,
            "truncated": False,
        },
    }


def mock_playback(monkeypatch):
    created = []
    image = np.zeros((240, 256, 3), dtype=np.uint8)

    class Env:
        def __init__(self):
            self.unwrapped = self
            self.ram = {0xCE: 176}
            self.index = len(created)
            created.append(self)

        def reset(self, seed):
            return image, {}

        def render(self):
            return image

        def close(self):
            pass

        def _get_info(self):
            return {"x_pos": 1, "world": 1, "stage": 1}

        def step(self, action):
            return image, 0, True, False, {"flag_get": self.index == 1}

    class Pipe(io.BytesIO):
        def close(self):
            pass

    class Encoder:
        def __init__(self, *args, **kwargs):
            self.stdin = Pipe()

        def wait(self):
            return 0

    monkeypatch.setattr(replay.gym_super_mario_bros, "make", lambda *a, **kw: Env())
    monkeypatch.setattr(replay, "JoypadSpace", lambda env, actions: env)
    monkeypatch.setattr(replay, "guard_final_cutscene", lambda env: None)
    monkeypatch.setattr(replay.subprocess, "Popen", Encoder)
    return created


@pytest.mark.parametrize("winning_only, expected_frames", [(False, 122), (True, 61)])
def test_video_filter_preserves_full_verification_and_retry_count(
    tmp_path, monkeypatch, capsys, winning_only, expected_frames
):
    created = mock_playback(monkeypatch)
    path = trace_file(
        tmp_path,
        [
            reset(),
            event("stage_start"),
            decision(1),
            event("stage_failure"),
            reset(),
            event("stage_start", attempt=2),
            decision(2, True),
            event("stage_clear", attempt=2),
        ],
    )
    args = [str(path), "--allow-incomplete", "--video", str(tmp_path / "mock.mp4")]
    replay.main(args + (["--winning-only"] if winning_only else []))
    result = json.loads(capsys.readouterr().out)
    assert len(created) == 2 and result["decisions"] == 2
    assert (
        result["environment_loads"] == 2
        and result["stage_loads"] == 1
        and result["retries"] == 1
    )
    assert result["video_frames"] == expected_frames
    assert result["video_mode"] == (
        "winning_stages_stitched" if winning_only else "chronological_all_attempts"
    )


def test_winning_video_still_rejects_divergence_in_omitted_failed_attempt(
    tmp_path, monkeypatch
):
    mock_playback(monkeypatch)
    path = trace_file(
        tmp_path,
        [
            reset(),
            event("stage_start"),
            decision(1, x=99),
            event("stage_failure"),
            reset(),
            event("stage_start", attempt=2),
            decision(2, True),
            event("stage_clear", attempt=2),
        ],
    )
    with pytest.raises(ValueError, match="Divergence"):
        replay.main(
            [
                str(path),
                "--allow-incomplete",
                "--video",
                str(tmp_path / "mock.mp4"),
                "--winning-only",
            ]
        )
