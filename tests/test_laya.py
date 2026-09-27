import json
from pathlib import Path

import httpx2

from mario_jev.laya import ModularLayaPolicy


def test_model_votes_control_jump_even_against_distance_rubric():
    # A genuine recorded state at a blocking pipe. No controller-side distance
    # threshold is allowed to replace a model vote for "absent/far".
    source = Path(__file__).parent / "fixtures" / "laya_wall.json"
    state = json.loads(source.read_text())
    profile = Path(__file__).parents[1] / "prompts/laya/v9.json"
    policy = ModularLayaPolicy("http://localhost", profile)
    requests = []
    vote = ["A"]

    def handle(request):
        body = json.loads(request.content)
        requests.append(body)
        assert str(state["mario"]["x"]) not in body["state"]
        assert "authorization" not in request.headers
        if "movement" in body["questions"]:
            answer = {"movement": {"choice": "run_right"}}
        else:
            answer = {"decision": {"choice": vote[0]}}
        return httpx2.Response(200, json={"answers": answer, "checkpoint": "test-laya"})

    policy.client.close()
    policy.client = httpx2.Client(
        base_url="http://localhost", transport=httpx2.MockTransport(handle)
    )
    action, _ = policy.choose(state)
    assert action == "right_run"
    vote[0] = "C"
    action, _ = policy.choose(state)
    assert action == "right_run_jump"
    assert len(requests) == 8
    policy.close()
