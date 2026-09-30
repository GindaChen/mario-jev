# Single-prompt CLM: World 1-1

The merged v21 prompt cleared the three-attempt fixed baseline and all 50
subsequent attempts with failure-only reflection enabled. Every attempt used
the same instructions string and frozen candidate descriptions. The runtime
had no separate memory field, note objects, retrieval or note clock.

| Measurement | 50-attempt run |
| --- | --- |
| Native clears | 50/50 |
| Prompt revisions / real S2 calls | 0 / 0 |
| Native frames / decisions verified | 96,700 / 26,800 |
| Frames / decisions per attempt | 1,934 / 536 |
| Selected actions per attempt | 527 right_jump; 9 right_run_jump |
| Automatic grounded A releases per attempt | 46 |
| Experiment elapsed time | 204.71 seconds |
| Cache-hit request latency p50 / p95 | 2.08 / 2.49 ms |

This prompt already contained lessons from prior failed attempts. It was not
optimized from scratch in this experiment. Since no attempt failed, the real
S2 rewrite path was never invoked; tests exercise proposal validation, review
and publication with mocked agent replies.

All 50 runs used the same checkpoint and seed 0 and produced identical action,
frame and RAM-hash sequences. All 26,800 requests hit the cache populated by the
three-attempt baseline. These are repeated executions of one learned behavior,
not a 100% generalization estimate. The first baseline attempt's 536 new encoding
requests measured p50/p95 29.47/31.14 ms. The fixed A-release helper remains part
of the controller, and the model's behavior remains overwhelmingly repetitive
jumping; native completion alone does not establish flexible reasoning.

## Inspect the evidence

- [Summary and latency accounting](evidence/summary.json), [all 50 attempt summaries](evidence/attempts.csv).
- [Full native replay audit](evidence/final.json): every saved request, controller action, image and RAM transition verified against the frozen runtime.
- [Single-prompt input audit](evidence/single-prompt-integrity.json): one prompt hash, frozen candidate descriptions and no note clock on every request.
- [Trace equality](evidence/trace-repetition.json): one distinct selected/executed-action and RAM-hash sequence across 50 attempts.
- [Original experiment manifest](evidence/experiment-manifest.json): protocol, limits, seed, model revisions and original source hashes.

The original archived run is on B200 at
`/raid/juc049/clm-mario/ablations/single-prompt-v21/experiments/reflection50`.
The companion baseline is `fixed3` in the same parent directory. Raw trajectories
and frames remain there; the files in this PR are compact audit outputs and
summaries, not a replacement for the complete archive.

## Source provenance and review scope

The initial import at commit `b00a20e3f7291320a45b14fcba13454d19782934`
formats the tested CLM code for review and extracts
`compact`, `atomic`, `FixedFrameFactory` and `CODEX_BIN` into `clm_support.py`
instead of importing the entire older `sync_v3` experiment. Existing
observation/controller files are byte-identical to the recorded run.

[Review source provenance](evidence/review-source-provenance.json) records the
original hashes and review hashes at that commit. At that commit, the five CLM
modules have identical executable
ASTs after ignoring imports and the explicit default `check=False` on subprocess
cleanup; the extracted helper functions match exactly. Historical replay audits
refer to the original frozen source hashes, not the formatted PR checkout.
Use the archive's own `frozen/` runtime when replaying historical traces.

The subsequent World 1-2 extension adds level selection, reset verification and
a text-only stage-hint policy. The historical import hashes above do not describe
those later edits. The [1-2 report](../clm-stage12-single-prompt/README.md) has a
separate source manifest and replay audit for its actual deployed runtime.

The new protocol does not change the game, model weights or scoring. This PR does
not publish a new website or include credentials/model weights. The
[implementation guide](../../CLM.md) contains prompts, entry points,
external S2 prerequisites and commands for a fresh run.
