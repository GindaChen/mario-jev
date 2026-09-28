"""Use DJev's endpoint with the original Mario questions and button rules."""

import json

import httpx2
from typesafe_sdk import RetryPolicy, TypeSafeClient

from .jev_modular import ModularJevPolicy
from .policy import JevPolicy


class DjevTransport(httpx2.BaseTransport):
    """Adapt the SDK route; preserve its typed response validation."""

    def __init__(self, inner=None, *, isolation="independent", api_path="/v1/request"):
        if api_path not in ("/v1/request", "/v1/systemone"):
            raise ValueError("Unsupported DJev API path")
        self.api_path = api_path
        if isolation not in ("joint", "independent"):
            raise ValueError("isolation must be joint or independent")
        self.isolation = isolation
        self.inner = inner if inner is not None else httpx2.HTTPTransport(retries=0)
        self.last_response = None
        self.inference_options = {}

    def handle_request(self, request):
        if request.url.path != "/v1/systemone":
            raise ValueError("DJev adapter only supports System One requests")
        body = json.loads(request.content)
        body["options"] = {
            "samples": 1,
            "seed": 0,
            "diagnostics": True,
            "isolation": self.isolation,
        }
        if self.api_path == "/v1/systemone":
            body.pop("options")
            body.update(samples=1, seed=0)
            body.update(self.inference_options)
            if self.isolation == "independent":
                for question in body["questions"].values():
                    question["alone"] = True
        headers = dict(request.headers)
        headers.pop("authorization", None)
        headers.pop("content-length", None)
        adapted = httpx2.Request(
            request.method,
            request.url.copy_with(path=self.api_path),
            headers=headers,
            json=body,
            extensions=request.extensions,
        )
        response = self.inner.handle_request(adapted)
        response.read()
        self.last_response = response.json() if response.is_success else None
        return response

    def close(self):
        self.inner.close()


class DjevPolicy(JevPolicy):
    def __init__(
        self,
        base_url="http://127.0.0.1:18341",
        *,
        isolation="independent",
        transport=None,
        profile=None,
        api_path="/v1/request",
    ):
        self.transport = DjevTransport(
            transport, isolation=isolation, api_path=api_path
        )
        client = TypeSafeClient(
            api_key="local-djev-unused",
            base_url=base_url,
            model="djev",
            timeout=60,
            retry=RetryPolicy(max_retries=0),
            transport=self.transport,
        )
        super().__init__(client=client, profile=profile)

    def choose(self, state):
        action, diagnostics = super().choose(state)
        diagnostics["backend"] = "djev"
        diagnostics["backend_diagnostics"] = self.transport.last_response.get(
            "diagnostics", {}
        )
        return action, diagnostics


class ModularDjevPolicy(ModularJevPolicy):
    """Local DJev with the same profile and observation contract as hosted Jev."""

    def __init__(
        self,
        base_url,
        profile,
        *,
        isolation="independent",
        transport=None,
        api_path="/v1/request",
    ):
        self.transport = DjevTransport(
            transport, isolation=isolation, api_path=api_path
        )
        client = TypeSafeClient(
            api_key="local-djev-unused",
            base_url=base_url,
            model="djev",
            timeout=60,
            retry=RetryPolicy(max_retries=0),
            transport=self.transport,
        )
        super().__init__("djev", profile, client=client)
        options = self.profile.get("inference", {})
        if set(options) - {"samples", "seed", "steps", "think"}:
            raise ValueError("Unknown DJev inference option")
        self.transport.inference_options = options

    def query(self, state_text, questions, calls):
        answers = super().query(state_text, questions, calls)
        calls[-1]["response"]["backend_diagnostics"] = self.transport.last_response.get(
            "diagnostics", {}
        )
        return answers
