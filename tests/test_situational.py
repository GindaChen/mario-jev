import copy
import json
from pathlib import Path

import httpx2
import pytest

from mario_jev.policy import ACTIONS
from mario_jev.situational import CRITERIA, SituationalDjevPolicy, observation

ROOT = Path(__file__).parents[1]
PROFILE = ROOT / "prompts/situational/1-3/v1.json"


def test_relative_observation_ignores_absolute_position_and_room():
    state = json.loads((ROOT / "tests/fixtures/laya_wall.json").read_text())
    state["action_frames"] = 4
    shifted = copy.deepcopy(state)
    shifted["mario"].update(x=9999, y=9999, feet_y=9999)
    shifted["room"] = {"area_data_address": 12345}
    for surface in shifted.get("landing_surfaces", {}).get("surfaces", []):
        surface["top_y"] += 100
    assert observation(state) == observation(shifted)


def test_fixed_menu_follows_model_except_approved_jump_release():
    calls = []
    selected = ["left"]

    def handle(request):
        body = json.loads(request.content)
        calls.append(body)
        return httpx2.Response(
            200,
            json={
                "model": "dgemma",
                "answers": {
                    "action": {
                        "type": "choice",
                        "choice": selected[0],
                        "confidence": 1.0,
                        "probabilities": {k: float(k == selected[0]) for k in CRITERIA},
                    }
                },
                "usage": {"input_tokens": 10, "output_tokens": 8},
            },
        )

    policy = SituationalDjevPolicy(
        "http://localhost", PROFILE, transport=httpx2.MockTransport(handle)
    )
    state = json.loads((ROOT / "tests/fixtures/laya_wall.json").read_text())
    state["action_frames"] = 4
    state["mario"]["grounded"] = True
    state["jump_already_held"] = False
    try:
        for name in ACTIONS:
            selected[0] = name
            action, _ = policy.choose(state)
            assert action == name
            assert calls[-1]["questions"]["action"]["criteria"] == CRITERIA
        selected[0] = "right_run_jump"
        state["jump_already_held"] = True
        action, record = policy.choose(state)
        assert action == "right_run"
        assert record["decisions"]["selected_action"] == "right_run_jump"
        assert record["requested_action_frames"] == 1
        assert calls[-1]["questions"] == calls[0]["questions"]
    finally:
        policy.close()


def test_profile_cannot_add_coordinate_routing_or_action_overrides(tmp_path):
    for key in ("memory_notes", "reflection_start_x", "criteria", "instruction_router"):
        data = json.loads(PROFILE.read_text())
        data[key] = {}
        path = tmp_path / "bad.json"
        path.write_text(json.dumps(data))
        with pytest.raises(ValueError, match="cannot configure"):
            SituationalDjevPolicy("http://localhost", path)
