"""CLM wire adapter for the existing reflection controller; no action policy added."""

import json
from pathlib import Path

import httpx2

from .reflection import ReflectionDjevPolicy


class ClmWireTransport(httpx2.BaseTransport):
    def __init__(self, inner=None, *, single_prompt=None):
        self.inner = inner or httpx2.HTTPTransport(retries=0)
        self.single_prompt = single_prompt
        self.last_request = None
        self.last_response = None

    def handle_request(self, request):
        if request.url.path != "/v1/systemone":
            raise ValueError("CLM only supports the System One route")
        original = json.loads(request.content)
        body = {
            "model": "clm-latest",
            "state": original["state"],
            "questions": {
                key: {
                    k: v
                    for k, v in q.items()
                    if k in ("type", "instructions", "criteria")
                }
                for key, q in original["questions"].items()
            },
        }
        if self.single_prompt is not None:
            # The shared legacy builder appends a newline even with zero notes.
            # Preserve the frozen prompt bytes and remove its unused note clock.
            if (
                set(body["questions"]) != {"action"}
                or body["questions"]["action"]["instructions"]
                != self.single_prompt + "\n"
            ):
                raise ValueError(
                    "Single-prompt input was changed by the legacy builder"
                )
            body["questions"]["action"]["instructions"] = self.single_prompt
            body["state"].pop("note_elapsed_frames", None)
        headers = {
            k: v
            for k, v in request.headers.items()
            if k not in ("authorization", "content-length")
        }
        self.last_request = body
        response = self.inner.handle_request(
            httpx2.Request(
                request.method,
                request.url,
                headers=headers,
                json=body,
                extensions=request.extensions,
            )
        )
        response.read()
        self.last_response = response.json() if response.is_success else None
        return response

    def close(self):
        self.inner.close()


class ClmReflectionPolicy(ReflectionDjevPolicy):
    """Keep legacy observation construction and explicit grounded A rearm unchanged."""

    def __init__(self, base_url, profile, *, transport=None):
        config = json.loads(Path(profile).read_text())
        single_prompt = None
        if config.get("single_prompt"):
            allowed = {
                "name",
                "mode",
                "one_frame_rearm",
                "single_prompt",
                "instructions",
                "criteria",
            }
            if set(config) != allowed:
                raise ValueError(
                    "Single-prompt profiles cannot contain notes or routers"
                )
            single_prompt = config["instructions"]
        self.wire = ClmWireTransport(transport, single_prompt=single_prompt)
        super().__init__(
            base_url, profile, api_path="/v1/systemone", transport=self.wire
        )

    def choose(self, state):
        action, diagnostics = super().choose(state)
        diagnostics["backend"] = "clm"
        diagnostics["actual_request"] = self.wire.last_request
        diagnostics["actual_response"] = self.wire.last_response
        return action, diagnostics
