"""Laya Mario worker atop the pinned decision-models-b200 runtime.

Run in /work of decision-models-gpu7; preserves the existing worker/services.
Unlike the latency worker this sends full candidate descriptions once and rejects
any input that would be truncated. Context extension does not prove accuracy.
"""

import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from laya.common import collate_items
from worker import Scorer

scorer = Scorer("laya")
app = FastAPI()


@app.get("/health")
def health():
    return {
        **scorer.runtime,
        "max_len": 8192,
        "head_max_len": 2048,
        "truncation": "rejected",
        "candidate_descriptions": "once",
    }


@app.post("/score")
def score(payload: dict):
    try:
        states, question, options = (
            payload["states"],
            payload["question"],
            payload["options"],
        )
        if len(states) != 1 or not 2 <= len(options) <= 16:
            raise ValueError("One state and 2-16 options required")
        tok = scorer.tok
        length = lambda s: len(tok.encode(s, add_special_tokens=False))
        if any(length(" " + o) > 48 for o in options):
            raise ValueError("Option exceeds native 48-token limit")
        head = length("choice question: " + question) + sum(
            1 + length(" " + o) for o in options
        )
        if head > 2048 or head + length(states[0]) + 4 > 8192:
            raise ValueError("Input exceeds full prompt budget; refusing truncation")
        internal = {
            "decision": scorer.agent._to_internal(
                {
                    "type": "choice",
                    "instructions": question,
                    "criteria": {o: "" for o in options},
                }
            )
        }
        enc = scorer.agent._encode_state(
            states[0], ["decision"], internal, max_len=8192, head_max_len=2048
        )
        batch = collate_items([enc], tok.pad_token_id)
        batch = {k: v.to("cuda") if torch.is_tensor(v) else v for k, v in batch.items()}
        probs = scorer.forward(batch, len(options))
        return {
            "model": "laya",
            "probabilities": [dict(zip(options, probs[0]))],
            "input_tokens_per_row": [len(enc[0]["ids"])],
            "truncation": False,
        }
    except Exception as exc:  # noqa: BLE001 -- HTTP error boundary
        raise HTTPException(400, f"{type(exc).__name__}: {exc}")


uvicorn.run(app, host="0.0.0.0", port=8821, log_level="warning", limit_concurrency=2)
