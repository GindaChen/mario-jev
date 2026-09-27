import json

import httpx2
import pytest

from mario_jev.scorer import ScorerPolicy


def test_complete_questions_and_same_button_logic(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "never-forward")
    requests = []

    def handle(request):
        assert "authorization" not in request.headers
        assert request.url.path == "/score/kev"
        payload = json.loads(request.content)
        requests.append(payload)
        options = payload["options"]
        p = [0.7, 0.1, 0.1, 0.1] if len(options) == 4 else [0.1, 0.9]
        return httpx2.Response(
            200,
            json={
                "model": "kev",
                "probabilities": [dict(zip(options, p))],
                "input_tokens_per_row": [100],
            },
        )

    policy = ScorerPolicy(
        "http://localhost", "kev", transport=httpx2.MockTransport(handle)
    )
    action, info = policy.choose(
        {"mario": {"grounded": True}, "jump_already_held": False}
    )
    assert action == "right_run_jump"
    assert len(requests) == 4
    assert requests[1]["question"] == policy.questions["start_jump"].instructions
    assert info["usage"]["input_tokens"] == 400
    assert len(info["backend_diagnostics"]) == 4
    policy.close()


def test_bad_distribution_is_error_not_fallback():
    def handle(request):
        options = json.loads(request.content)["options"]
        return httpx2.Response(
            200, json={"model": "kev", "probabilities": [dict.fromkeys(options, 0.9)]}
        )

    policy = ScorerPolicy(
        "http://localhost", "kev", transport=httpx2.MockTransport(handle)
    )
    with pytest.raises(ValueError, match="distribution"):
        policy.choose({})
    policy.close()


def test_laya_requires_nontruncating_worker():
    with pytest.raises(ValueError, match="non-truncating"):
        ScorerPolicy("http://localhost", "laya")


def test_wrong_model_is_rejected():
    def handle(request):
        return httpx2.Response(200, json={"model": "laya", "probabilities": [{}]})

    policy = ScorerPolicy(
        "http://localhost", "kev", transport=httpx2.MockTransport(handle)
    )
    with pytest.raises(ValueError, match="wrong model"):
        policy.choose({})
    policy.close()
