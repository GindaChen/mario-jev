"""Shared model-driven controller; each backend selects all tactical cases."""

from .laya import ModularLayaPolicy


class ModularCandidatePolicy(ModularLayaPolicy):
    def __init__(self, base_url, profile, model):
        super().__init__(base_url, profile)
        self.model = model

    def query(self, state_text, questions, calls):
        payload = {"state": state_text, "questions": questions}
        response = self.client.post("/decide", json=payload)
        if not response.is_success:
            raise RuntimeError(
                f"{self.model} {response.status_code}: {response.text[:2000]}"
            )
        result = response.json()
        if result.get("model") != self.model:
            raise ValueError("Backend model identity mismatch")
        for key, question in questions.items():
            if result["answers"][key]["choice"] not in question["criteria"]:
                raise ValueError("Backend returned an unknown choice")
        calls.append({"request": payload, "response": result})
        return result["answers"]
