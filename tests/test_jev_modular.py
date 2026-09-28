import json
from pathlib import Path

import httpx2
import pytest
from typesafe_sdk import TypeSafeClient

from mario_jev.jev_modular import ModularJevPolicy


@pytest.mark.parametrize("profile", ["v4", "v9", "v12", "v13", "v15", "d1", "d5", "d8", "d11"])
def test_native_jev_votes_control_jump(monkeypatch, profile):
    monkeypatch.setenv("TYPESAFE_API_KEY", "test-key")
    root = Path(__file__).parents[1]
    state = json.loads((root / "tests/fixtures/laya_wall.json").read_text())
    state.setdefault("landing_surfaces", {"surfaces": [], "floor_gaps": []})
    policy = ModularJevPolicy(
        "jev-1.13.0",
        root / f"prompts/{'djev' if profile.startswith('d') else 'jev'}/{profile}.json",
    )
    vote = ["A"]
    movement = ["run_right"]
    calls = []

    def handle(request):
        body = json.loads(request.content)
        calls.append(body)
        assert body["model"] == "jev-1.13.0"
        assert '"x":' not in json.dumps(body["state"])
        answers = {}
        for key, question in body["questions"].items():
            choice = movement[0] if key == "movement" else vote[0]
            answers[key] = {
                "type": "choice",
                "choice": choice,
                "confidence": 0.9,
                "probabilities": {k: float(k == choice) for k in question["criteria"]},
            }
        return httpx2.Response(
            200,
            json={
                "model": "jev-1.13.0",
                "answers": answers,
                "usage": {"input_tokens": 100, "output_tokens": 10},
            },
        )

    policy.client.close()
    policy.client = TypeSafeClient(
        api_key="test-key", model="jev-1.13.0", transport=httpx2.MockTransport(handle)
    )
    try:
        assert policy.choose(state)[0] == "right_run"
        vote[0] = "C"
        action, info = policy.choose(state)
        assert action == "right_run_jump"
        assert info["model"] == "jev-1.13.0"
        assert len(calls) == 8
        if profile == "v15":
            movement[0] = "dodge_left"
            action, info = policy.choose(state)
            assert action == "left_jump"
            assert info["decisions"]["movement"] == "dodge_left"
    finally:
        policy.close()
