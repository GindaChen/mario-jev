import json

import httpx2
import pytest
from typesafe_sdk import TypeSafeInternalServerError

from mario_jev.djev import DjevPolicy


@pytest.mark.parametrize("isolation", [None, "joint"])
def test_djev_route_and_original_controller(monkeypatch, isolation):
    monkeypatch.setenv("TYPESAFE_API_KEY", "must-not-be-forwarded")

    def handle(request):
        assert request.url.path == "/v1/request"
        assert "authorization" not in request.headers
        body = json.loads(request.content)
        assert body["model"] == "djev"
        assert body["options"] == {
            "seed": 0,
            "samples": 1,
            "diagnostics": True,
            "isolation": isolation or "independent",
        }
        assert set(body["questions"]) == {
            "movement",
            "start_jump",
            "ceiling_hop",
            "sustain_jump",
        }
        return httpx2.Response(
            200,
            json={
                "model": "djev-0.1",
                "usage": {"input_tokens": 42, "output_tokens": 20},
                "answers": {
                    "movement": {
                        "type": "choice",
                        "choice": "run_right",
                        "confidence": 0.8,
                        "probabilities": {"run_right": 0.9},
                    },
                    "start_jump": {"type": "noul", "noul": 0.1},
                    "ceiling_hop": {"type": "noul", "noul": 0.9},
                    "sustain_jump": {"type": "noul", "noul": 0.1},
                },
                "diagnostics": {"calibration": "unvalidated"},
            },
        )

    kwargs = {} if isolation is None else {"isolation": isolation}
    policy = DjevPolicy(transport=httpx2.MockTransport(handle), **kwargs)
    try:
        action, info = policy.choose(
            {
                "mario": {"grounded": True},
                "jump_already_held": False,
                "jump_corridor": {"low_ceiling_before_nearest_threat": True},
            }
        )
        assert action == "right_run_jump"
        assert info["decisions"]["jump_timing_source"] == "ceiling_hop"
        assert info["model"] == "djev-0.1"
        assert info["backend_diagnostics"]["calibration"] == "unvalidated"
    finally:
        policy.close()


def test_djev_failure_is_not_retried():
    calls = []

    def handle(request):
        calls.append(request)
        return httpx2.Response(503, json={"error": {"message": "unavailable"}})

    policy = DjevPolicy(transport=httpx2.MockTransport(handle))
    try:
        with pytest.raises(TypeSafeInternalServerError):
            policy.choose({})
        assert len(calls) == 1
    finally:
        policy.close()
