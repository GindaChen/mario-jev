"""Independent candidate scoring using the decision-model HTTP workers.

Boolean probabilities are binary choice scores, not calibrated Jev Noul values.
"""

import json
import math
from types import SimpleNamespace

import httpx2

from .policy import JevPolicy

MODELS = ("laya", "kev", "nimble", "openjev4", "openjev35")


class ScorerClient:
    def __init__(self, base_url, model, *, direct=False, transport=None):
        if model not in MODELS:
            raise ValueError(f"Unsupported scorer: {model}")
        if model == "laya" and not direct:
            raise ValueError(
                "Laya requires --scorer-direct and the non-truncating Mario worker URL"
            )
        self.model = model
        self.route = "/score" if direct else f"/score/{model}"
        self.http = httpx2.Client(base_url=base_url, timeout=120, transport=transport)
        self.last = {}

    def system_one(self, *, state, questions):
        answers = {}
        self.last = {}
        for name, question in questions.items():
            criteria = getattr(question, "criteria", None)
            # Keep option IDs and their full descriptions together for scorers
            # whose API accepts candidate strings rather than a criteria mapping.
            options = (
                [f"{key}: {description}" for key, description in criteria.items()]
                if criteria
                else ["false", "true"]
            )
            payload = {
                "states": [json.dumps(state, separators=(",", ":"))],
                "question": question.instructions,
                "options": options,
            }
            response = self.http.post(self.route, json=payload)
            if not response.is_success:
                raise RuntimeError(
                    f"Scorer HTTP {response.status_code}: {response.text[:2000]}"
                )
            result = response.json()
            if result.get("model") != self.model or len(result["probabilities"]) != 1:
                raise ValueError("Scorer returned the wrong model or batch size")
            probabilities = result["probabilities"][0]
            values = [probabilities[o] for o in options]
            if (
                set(probabilities) != set(options)
                or any(not math.isfinite(p) or not 0 <= p <= 1 for p in values)
                or not math.isclose(sum(values), 1, abs_tol=1e-4)
            ):
                raise ValueError("Invalid candidate probability distribution")
            self.last[name] = {"request": payload, "response": result}
            if criteria:
                probs = dict(zip(criteria, values, strict=True))
                choice = max(probs, key=probs.get)
                answers[name] = SimpleNamespace(
                    choice=choice, confidence=probs[choice], probabilities=probs
                )
            else:
                answers[name] = SimpleNamespace(noul=probabilities["true"])
        return SimpleNamespace(
            answers=answers,
            model=self.model,
            usage=SimpleNamespace(
                input_tokens=sum(
                    sum(r["response"]["input_tokens_per_row"])
                    for r in self.last.values()
                ),
                output_tokens=0,
            ),
        )

    def close(self):
        self.http.close()


class ScorerPolicy(JevPolicy):
    def __init__(self, base_url, model, *, direct=False, transport=None):
        super().__init__(
            client=ScorerClient(base_url, model, direct=direct, transport=transport)
        )

    def choose(self, state):
        action, diagnostics = super().choose(state)
        diagnostics.update(
            backend="candidate-scorer", backend_diagnostics=self.client.last
        )
        return action, diagnostics
