"""Check true/false score orientation independently of Mario's long prompts."""

import json
from pathlib import Path

from typesafe_sdk import Noul

from mario_jev.scorer import MODELS, ScorerClient

results = []
for model in MODELS:
    client = ScorerClient(
        "http://127.0.0.1:18821" if model == "laya" else "http://127.0.0.1:18797",
        model,
        direct=model == "laya",
    )
    try:
        for value, expected in [("ON", True), ("OFF", False)]:
            answer = (
                client.system_one(
                    state={"switch": value},
                    questions={"answer": Noul(instructions="Is the switch ON?")},
                )
                .answers["answer"]
                .noul
            )
            result = {
                "model": model,
                "switch": value,
                "expected": expected,
                "probability_true": answer,
                "correct": (answer >= 0.5) == expected,
                "trace": client.last,
            }
            results.append(result)
            print(model, value, answer, result["correct"], flush=True)
    finally:
        client.close()
Path("runs/other-models/sanity.json").write_text(json.dumps(results, indent=2) + "\n")
