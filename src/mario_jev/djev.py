"""Use DJev's endpoint with the original Mario questions and button rules."""

import json

import httpx2
from typesafe_sdk import RetryPolicy, TypeSafeClient

from .policy import JevPolicy


class DjevTransport(httpx2.BaseTransport):
    """Adapt the SDK route; preserve its typed response validation."""

    def __init__(self, inner=None, *, isolation="independent"):
        if isolation not in ("joint", "independent"):
            raise ValueError("isolation must be joint or independent")
        self.isolation = isolation
        self.inner = inner if inner is not None else httpx2.HTTPTransport(retries=0)
        self.last_response = None

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
        headers = dict(request.headers)
        headers.pop("authorization", None)
        headers.pop("content-length", None)
        adapted = httpx2.Request(
            request.method,
            request.url.copy_with(path="/v1/request"),
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
    ):
        self.transport = DjevTransport(transport, isolation=isolation)
        client = TypeSafeClient(
            api_key="local-djev-unused",
            base_url=base_url,
            model="djev",
            timeout=60,
            retry=RetryPolicy(max_retries=0),
            transport=self.transport,
        )
        super().__init__(client=client)

    def choose(self, state):
        action, diagnostics = super().choose(state)
        diagnostics["backend"] = "djev"
        diagnostics["backend_diagnostics"] = self.transport.last_response.get(
            "diagnostics", {}
        )
        return action, diagnostics
