# Mario simulation and DJev inference on AMD

Both now run on `mlsys-amd.ucsd.edu`:

- Emulator and harness: `/home/juc049/projects/mario-amd/harness` (CPU).
- DJev structured API: `http://127.0.0.1:18515/v1/systemone`.
- Model worker: `djev-amd-gpu7-model`, served as `dgemma`; model config identifies
  `DiffusionGemmaForBlockDiffusion`, BF16, no quantization config.
- Inference is on physical GPU7 (`HIP_VISIBLE_DEVICES=4`, PCI F5:00.0).
- Existing GPU7 model services share the device. No model restart was required.
- DJev uses no hosted Jev key; the transport strips authorization headers.
- Hosted Jev remains a different backend. Its earlier trials used the Mac
  emulator and TypeSafe's remote API; those results are recorded separately.

From the Mac:

```sh
ssh amd 'cd /home/juc049/projects/mario-amd/harness && scripts/run_amd_djev.sh'
```

The wrapper runs world 1-2. Override the profile with `--djev-profile PATH`.
Each decision logs the actual returned model, probabilities, exact state/questions,
profile hash, and DJev backend timing/label diagnostics. API adapter settings:
one sample, seed 0, independent questions, `/v1/systemone` endpoint. One inference
step is the server default and appears in each response's diagnostics.

The previous B200 DJev adapter used `/v1/request` and nested `options`. AMD's
current API uses `/v1/systemone` and top-level `samples`, `seed`, and per-question
`alone`. Both versions are supported explicitly by `--djev-api-path`.

To watch a recorded AMD run on the Mac, copy its trace into the local `runs/`
directory and use `.venv/bin/mario-jev --replay TRACE.jsonl`.
The emulator reconstructs the recorded actions; it does not call the model.

The 30-run tuning budget is finished: **0/30 fresh world 1-2 completions**.
There were 16 completed hosted Jev trials and 14 AMD-local DJev trials, plus one
hosted API 503 interruption that was excluded from the gameplay budget. All 30
completed traces replayed exactly. Machine-readable results are in
`jev-1-2-tuning-results.json`; replay verification is in
`jev-1-2-replay-verification.json`.

| Backend | Best profile | Furthest x | Result |
|---|---|---:|---|
| Hosted Jev 1.13.0 | v16 |1646| Died before completion |
| AMD DJev/dgemma | d1 |1331| Died before completion |

These are adaptive integration trials, with different prompts and observation
variants, not a controlled model ranking. One trial used two-frame actions;
the others used four. All started fresh; no winning action sequence was supplied.
The model selected movement and jump votes; ordinary button composition and
jump rearming stayed in the harness. Prompts use relative geometry, not stage
coordinates. All attempted profiles and exact requests are preserved.

The repeated failure modes were the low-ceiling raised-platform passage,
falling enemies, and timing a jump under a ceiling before a floor gap. The best
hosted run also hit a piranha plant while landing. DJev returned different
probabilities for identical requests in trials 22/23 despite the configured
seed, so individual regressions cannot all be attributed to prompt changes.

Across all 14 completed AMD trials: 2425 decisions, 7072 individual queries.
Median decision latency was 132.49 ms (p95 259.31 ms); median server query time
was 59.99 ms (p95 64.57 ms). Decision latency includes multiple sequential model
questions. These are synchronous controller timings, not a 60 FPS game-rate claim.
See `amd-djev-latency.json` for the aggregate metrics.

Validation: 51 tests passed on both Mac and AMD; Ruff and diff whitespace checks
passed locally. No GPU or model service restart was needed. No hosted API key
was transferred.

To replay the best DJev attempt locally:

```sh
.venv/bin/mario-jev --replay runs/djev-1-2-tuning/19-d1/20260927T230224133896Z.jsonl
```


## Follow-up: System 2 reflection succeeded

The separate 100-attempt reflection study subsequently passed world1-2, with
20/20 frozen validation wins. The AMD wrapper now defaults to r35. The 0/30
results above describe the earlier experiment. See [reflection results](reflection/README.md).
