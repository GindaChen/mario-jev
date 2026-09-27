# Mario: five additional decision models

Test date: 2026-09-26, America/Los_Angeles. Inference used the existing B200 GPU 7 services; this was not an AMD deployment.

**None of the five new models completed World 1-1 in this run. Laya progressed farthest.** The saved Jev and corrected DJev baselines completed the same configuration.

| Model | Completed | Maximum x | Decisions | Stop |
|---|---|---:|---:|---|
| Jev (saved baseline) | Yes | 3161 | 351 | Flag reached |
| DJev independent (saved baseline) | Yes | 3161 | 362 | Flag reached |
| Laya 421M | No | 1795 | 168 | terminated |
| Bespoke Nimble 9B | No | 1123 | 252 | terminated |
| Kev 0.5B | No | 596 | 500 | decision_limit |
| OpenJev 35B-A3B | No | 435 | 500 | decision_limit |
| OpenJev 4B v5 | No | 299 | 32 | terminated |

## What was held fixed

One episode per model: SuperMarioBros-1-1-v0, seed 123, four frames per action (with the original landing interruption), 12 transitions of history, and a 500-decision cap. The emulator pauses for inference. Same RAM observation, four question instructions, action choices, and button rules as the Jev controller. No gameplay prompt tuning or threshold changes were made after seeing these results.

Each scorer evaluates the four questions independently. The three Noul questions are adapted to binary false/true choice scoring, then use the original 0.5 threshold. These are not calibrated Jev Noul probabilities. Candidate descriptions are retained; native model formatting differs. OpenJev normalizes entailment scores across candidates using its reference decision template.

Laya uses convaiinnovations/laya, not laya-typed-decisions. Kev uses jaredpalmer/kev-0.5b, not Kev-9B. Full-generation DiffusionGemma was not tested. These results must not be generalized to those other checkpoints.

Laya runs in a separate worker with an 8192-token total budget and 2048-token question budget. Oversized states/questions and options exceeding its native 48-token limit are rejected. This avoids silently dropping Mario instructions, but extends beyond the checkpoint default context setting; long-context accuracy is unvalidated. Other workers reject oversized inputs.

## Observed failures

- **Laya 421M:** Died in Goomba contact after landing under low bricks.
- **Bespoke Nimble 9B:** Descended too low at the first pit and failed to land on the far bank.
- **Kev 0.5B:** Repeated short jumps failed to clear the pipe; reached the decision limit.
- **OpenJev 35B-A3B:** Walked into the first pipe without starting a jump; reached the decision limit.
- **OpenJev 4B v5:** Died near the first Goomba.

## Verification and artifacts

All five gameplay processes exited normally with complete episode summaries; no serving errors were counted as deaths. All five traces replayed with every recorded decision position matching. All ten ON/OFF controls passed (one positive and one negative per scorer). The adapter test suite has 35 passing tests. These controls check orientation and execution, not broad model quality or long-context reasoning.

One deterministic episode is not a success-rate benchmark or a general model ranking. Failures can reflect the observation format, native prompt conversion, score calibration, and control timing as well as the model.

Checkpoint revisions: [scorer-provenance.json](scorer-provenance.json). Machine-readable outcomes: [scorer-results.json](scorer-results.json). Raw traces, exact scorer requests/responses, runtime metadata, sanity controls, and replay outputs are retained locally under `runs/other-models/` (git-ignored).

| Model | Median decision latency (ms) | Largest input row (tokens) | Local trace |
|---|---:|---:|---|
| Kev 0.5B | 204.8 | 3650 | `runs/other-models/kev/20260927T023409552753Z.jsonl` |
| Laya 421M | 428.5 | 4089 | `runs/other-models/laya/20260927T024648078998Z.jsonl` |
| Bespoke Nimble 9B | 511.7 | 4050 | `runs/other-models/nimble/20260927T023603333316Z.jsonl` |
| OpenJev 35B-A3B | 912.0 | 3652 | `runs/other-models/openjev35/20260927T023850246543Z.jsonl` |
| OpenJev 4B v5 | 552.3 | 3618 | `runs/other-models/openjev4/20260927T023812514102Z.jsonl` |

Latency includes four serial requests, tokenization, inference, and SSH transport. Services share GPU 7; these are gameplay timings, not isolated inference benchmarks.

## Run and replay

From this repository, with the gateway tunnel active:

```sh
uv run mario-jev --policy scorer --model nimble --headless --decisions 500 --log-every 25
```

Replay the farthest new-model run without model calls:

```sh
uv run mario-jev --replay runs/other-models/laya/20260927T024648078998Z.jsonl
```

Laya requires the separate non-truncating worker and `--scorer-direct --scorer-url http://127.0.0.1:18821`; see the README. Existing Jev/DJev traces were reused for the baseline, not fresh API runs. Baseline files: `runs/20260926T211534147249Z.jsonl` and `runs/20260926T221401248810Z.jsonl`.
