# Mario 1-1 on AMD GPU 7 — 2026-09-27

The emulator, harness, and four model workers now run on `amd` under
`/home/juc049/projects/mario-amd`. Original B200 files were preserved.
This migration covers Laya, Kev, Nimble, and OpenJev-4B. OpenJev-35B was not
provisioned or evaluated in this pass.

| Model | Profile | Fresh results | Decisions to finish |
|---|---|---|---|
| Laya | laya/v9 | 1/1 passed | 308 |
| Nimble | laya/v9 | 2/2 passed | 422 each |
| OpenJev-4B | modular/v10 | 2/2 passed | 307 each |
| Kev | modular/v10–v13 plus laya/v9 | 0/5 passed; best x=1128 | — |

The flag was reached at x=3161. Replays of the first winning run for each
successful model matched every recorded position. These are repeated tests of
the same deterministic level/seed, not evidence of generalization to other levels.
All 41 tests pass locally and on AMD; Ruff passes for changed Python files.
Full run summaries and runtime provenance: [amd-results.json](amd-results.json).
Full requests, probabilities, observations, actions, and timings are in `runs/amd-*`
on both machines (ignored by Git). Failures are retained.

## What changed

Added `/decide` adapters for native Kev candidate scoring, Nimble's published
candidate-token scoring, and OpenJev NLI scoring. Each returns model identity,
pinned checkpoint, candidate probabilities, token counts, and service time.
Candidate descriptions occur once. Over-budget inputs are rejected; no silent
truncation. The harness checks model identity and returned choice keys.

Nimble succeeds with Laya's original modular profile. OpenJev needed movement
separated from hazard observations: it chooses forward movement toward the goal,
while separate model queries classify enemy/wall/pit spacing and vertical motion.
Kev improved from x=209 to x=1128 with explicit count descriptions but continues
to misclassify distances; enumerating far distances regressed to x=681.

All live decisions use the selected model. Human-written prompts supply the
same jump-distance rubric as Laya; code maps model-selected cases to buttons.
No level-coordinate action script, prerecorded live policy, model-weight update,
ROM modification, or alternate model selecting actions was introduced. Grounded
button rearming remains a mechanical guard. Tests explicitly verify that model
votes override the distance rubric even at a blocking wall.

## GPU and services

Physical GPU 7 is PCI `0000:F5:00.0`, **HIP ordinal 4** on this host.
Use `HIP_VISIBLE_DEVICES=4`; 7 would select the wrong physical GPU.
The new workers coexist with the existing DJev replica on GPU 7. GPUs 0–6 and
the existing replica were not stopped. GPU 7 is therefore not exclusive to Mario.
Do not interpret these concurrent trial timings as an isolated GPU benchmark.

| Worker container | AMD localhost port |
|---|---:|
| mario-laya-amd-gpu7 | 18821 |
| mario-kev-amd-gpu7 | 18822 |
| mario-nimble-amd-gpu7 | 18823 |
| mario-openjev4-amd-gpu7 | 18824 |

Containers restart unless stopped. Logs: `docker logs CONTAINER`.
The temporary download container `mario-amd-gpu7` is stopped.
Runtime: pinned image `sha256:03a63c57bce6b7f45bd4845d306a73f037ff4877d322a1474362ac97614900ae`,
Torch 2.12.0+git6bbd260, ROCm 7.2, Transformers 5.17.0. Weights are BF16 except
Laya's FP32 stored weights/BF16 autocast and Kev's FP32 pointer head. No FP4.
Nimble/OpenJev currently use reference fallbacks without FLA/causal-conv1d.

## Run on AMD

```sh
ssh amd
cd /home/juc049/projects/mario-amd/harness
.venv/bin/mario-jev --policy modular --model nimble \
  --decision-url http://127.0.0.1:18823 \
  --decision-profile prompts/laya/v9.json --headless
.venv/bin/mario-jev --policy modular --model openjev4 \
  --decision-url http://127.0.0.1:18824 \
  --decision-profile prompts/modular/v10.json --headless
.venv/bin/mario-jev --policy laya --laya-url http://127.0.0.1:18821 \
  --laya-profile prompts/laya/v9.json --headless
# Kev's best attempted profile, still unsuccessful:
.venv/bin/mario-jev --policy modular --model kev \
  --decision-url http://127.0.0.1:18822 \
  --decision-profile prompts/modular/v12.json --headless
```

`serving/start_amd.sh` starts existing workers or recreates missing containers
using the already provisioned runtime directory and pinned image. It validates
GPU mapping first; it is not a fresh-machine installer. Source dependencies,
model snapshots and pinned HF manifest live in `../runtime/`. `worker.py` and
model source packages came from the existing decision-models runtime;
`mario_worker.py` is `serving/reference_worker.py`, and `modular_worker.py` is
`serving/modular_worker.py`. Update those mounted files before restarting a
worker when changing its implementation.
