# CLM single-prompt transfer to World 1-2

The first transferred prompt did **not** clear 1-2: **0/3 clears**, with all three
attempts dying at x=198. CLM selected `right_run` on every decision, approaching
the first Goomba without jumping. The controller executed exactly those choices.
This is evidence about this prompt, not proof that CLM cannot clear the level.

| Measurement | Result |
| --- | --- |
| Level / seed | World 1-2 / 0 |
| Attempts / native clears | 3 / 0 |
| Maximum x in each attempt | 198 |
| Decisions / native frames per attempt | 20 / 74 |
| Selected and executed actions per attempt | 20 `right_run` |
| Automatic A releases / other overrides | 0 / 0 |
| Distinct instruction strings / real S2 calls | 1 / 0 |
| Uncached request latency p50 / p95 (20 requests) | 30.82 / 35.77 ms |
| Cache-hit latency p50 / p95 (40 requests) | 2.27 / 2.81 ms |

These use the same reset checkpoint and deterministic cached scorer. Repeated
failures are reproducibility checks, not three independent model samples.
The evaluator starts at native World 1-2 and advances at most four frames after
each model response. This is a stage-specific trial, not a continuous 1-1 to 1-2 run.

## Exact prompt and prior experience

The [4,781-character prompt](../../prompts/clm/single-prompt-1-2/template/initial-instructions.md)
combines v21's base instructions (changing the level name) with four lessons from
the older DJev `r35-plant-timing` 1-2 profile. It does not include v21's 1-1 failure
notes. The eight candidate descriptions are unchanged from the CLM v21 source.

All four lessons are included at every step. Their applicability ranges are
ordinary text for CLM to interpret: escape-ledge x940–1020, pit-approach
x1220–1259, pit-takeoff x1260–1325, and plant-cycle-wait x1390–1490.
There is no host-side region activation. The old sticky retreat becomes textual
guidance using observed action history. The old 60-frame plant-note countdown
is replaced by an untested observation-based waiting hypothesis, because this
protocol has no note timer. The [lesson provenance](../../prompts/clm/single-prompt-1-2/lesson-provenance.json)
records these adaptations. Earlier success with DJev's different observation and
note-retrieval setup does not establish that this transfer will work for CLM.

The base prompt already says to jump before an approaching same-height enemy.
Nevertheless, at native frame 73, the recorded request reports an enemy ahead
at dx=7, gap=0 and contact estimate=0 frames; CLM scores `right_run` at about
0.722 versus `right_run_jump` at about 0.117. The next native frame ends in death.
The more distant lesson regions are never reached. See the
[complete final decision, request and response](evidence/attempt-0001-final-decision.json).

The [S2 template](../../prompts/clm/single-prompt-1-2/template/system2-instructions.md)
is ready for failure-only prompt revision, but this pilot used `--fixed` and made
no S2 calls. No prompt was changed after observing these results.

## Controller authority

The active single-prompt path has no coordinate, zone, obstacle or enemy rule
that overrides the model's chosen action. It always offers the same eight
candidates. The shared library retains legacy note-activation/fallback code for
other experiments; the strict single-prompt schema rejects fields that enable
it. A regression test tries all eight model choices at twelve old note boundaries
and fails if either legacy path is called.

There is one declared general controller aid: if Mario is grounded, A was already
held and the model chooses an A-containing action, the controller removes A for
one native frame to re-arm a later jump. It never adds A or decides where to jump.
Landing can end a four-frame action early; death and stall limits can stop an
attempt. These mechanics are retained from the 1-1 experiment and are not learned.
The A-release aid was unused in this 1-2 pilot.

The host selects the level only at reset, checks the native world/stage, and
records the checkpoint hash. It does not route in-episode actions by level.
Prompt text may contain conditional stage hints; CLM is responsible for applying
them. Neither model can change the emulator, observation code, scoring or controller.

## Audits and reproducibility

- [Native replay](evidence/final.json): all **60 decisions / 222 native frames** pass exact-request, image and full-RAM verification.
- [Input integrity](evidence/single-prompt-integrity.json): one prompt hash, frozen candidates, no note clock, and zero agent workspaces.
- [Action authority](evidence/action-authority.json): every executed key equals CLM's selected keys; **zero other overrides**. The [post-hoc audit script](audit_action_authority.py) does not consult coordinates, zones, enemies or timers.
- [Metrics](evidence/metrics.json), [attempt summaries](evidence/attempts.csv), and [runtime manifest](evidence/experiment-manifest.json).

Exact prompt SHA-256:
`07d83ee8f2d39ecc806525397e42d4898e75c537f1d5aab66ff52ab6d54c3dac`.
The manifest records the exact deployed source and model hashes. Source replay
checks reject drift; use this run's frozen runtime to replay it later.

The complete archive, including all requests, frame images, source snapshots and
the RAM-verified 60 FPS video, is on B200 at
`/raid/juc049/clm-mario/stage12-single-prompt/experiments/fixed3`.
Its bounded service completed successfully and is inactive. A local copy is in
the ignored `deliverables/clm-stage12-single-prompt/run/` directory. Git contains
compact evidence and one full decision; raw frames and video remain outside Git.
The public website has not been updated with this pilot.

Use the [1-2 command in CLM.md](../../CLM.md#try-world-1-2) to reproduce the fixed
pilot. For a future prompt-optimization run, omit `--fixed` only after configuring
the documented external S2 infrastructure and choose a fresh run name.
