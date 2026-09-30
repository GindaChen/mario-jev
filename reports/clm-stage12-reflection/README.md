# World 1-2: single-prompt reflection did not clear

The corrected run finished **25 attempts with 0 clears** before the original
one-hour aggregate deadline. S2 published 24 prompt revisions. Best progress was
**x=822 on attempt 16, prompt v15**; later revisions regressed. This is a failed
bounded prompt-optimization run, not evidence that CLM can never clear 1-2.

All **2,416 decisions / 8,997 native frames** passed exact-request and full-RAM
replay. Executed keys matched CLM's choices except for **171 declared one-frame
A releases**. No other action overrides or host-side region routing were found.
The controller did not insert a moving jump to rescue play.

## Protocol and separate segments

World 1-2, reset seed 0, CLM-v0.1-8B with the pinned Qwen3-8B encoder, one immutable
instructions string per attempt, eight frozen candidate descriptions. CLM runs
in lockstep with the emulator, holding each selected action for at most four
native frames and observing early on landing. S2 uses `gpt-6-sol` / medium,
reflecting only after failure. It can read full archived observations, images and
traces, and revise instructions. Conditional coordinate hints are permitted as
ordinary text present in every request. Code routing, replay and action schedules
are forbidden. The fixed A-release helper is disclosed rather than learned.

The initial prompt is the [same 4,781-character transfer prompt](../../prompts/clm/single-prompt-1-2/template/initial-instructions.md)
as the earlier fixed pilot: v21 base guidance plus four older DJev 1-2 lessons.
This is a warm start, not a memory-free or from-scratch test.

| Segment | Completed attempts | Result | Treatment |
| --- | ---: | --- | --- |
| Earlier `fixed3` pilot | 3 | 0 clears; all died at x=198 | Separate, before this reflection budget |
| `reflection50` | 3 | 0 clears; all died at x=198 | Stopped for reviewer-reference repair; retained separately |
| `reflection-reviewfix` | 25 | 11 deaths, 14 stalls; best x=822 | Corrected run reported here |

There were **28 gameplay attempts within the reflection experiment's aggregate
budget**, including the interrupted segment. They must not be presented as one
homogeneous 28-trial batch. The [repair record](OPERATIONS.md) explains the false
reviewer rejection, commit `b308feb`, and fresh restart from the original prompt.
No human wrote a replacement gameplay prompt during the run.

## What actually happened

CLM selected only two actions across the entire corrected run:

| Model-selected action | Count | Execution |
| --- | ---: | --- |
| `jump` (A only) | 2,214 | 2,043 A-only actions; 171 one-frame release/wait actions |
| `right_run` (Right+B) | 202 | Executed as selected |
| All six other candidates | 0 | Includes zero `right_run_jump` and zero `right_jump` choices |

Thirteen attempts stalled at the opening x=40. Seven died at x=198 after choosing
`right_run` on every decision. The other deaths ended at x=76, 93, 179 and 822;
one later attempt stalled at x=482. The [attempt table](evidence/attempts.csv)
records every outcome, prompt version, latency and helper count.

S2 repeatedly clarified opening movement, enemy takeoff distance, and the need
for horizontal input while jumping. Its hypotheses were trace-based, but the
scorer frequently continued jumping in place or running into the first enemy.
The best attempt used **234 `jump` + 32 `right_run` selections**, with 21 A
releases; it died near a Koopa and low brick span. S2 then added a conditional
hint for that obstacle, but the next two attempts regressed to opening stalls.
Attempt 24 reached x=482 and stalled beside a raised block. Its resulting prompt
v24 died at x=179 on attempt 25.

These traces do not demonstrate reliable interpretation of the conditional
instructions. Progress alone does not establish which sentence affected the
model. There is also **no performance keep/revert gate**: publication checks
integrity, not improvement. The final prompt is v24; the best observed prompt is
v15, and it was not revalidated in fresh trials.

## Exact prompts and S2 evidence

- [All 25 exact prompts, v0–v24](prompts/README.md), including [best v15](prompts/v0015.md) and [last v24](prompts/v0024.md).
- [Prompt hashes, hypotheses and publication verdicts](evidence/prompt-revisions.json).
- [Frozen action descriptions](evidence/frozen-criteria.json), unchanged across all attempts.
- [S2 log inventory](evidence/s2-log-inventory.json) and [events](evidence/events.jsonl), including failed/retried turns.
- [Semantic supervision findings](evidence/final-supervision.json).

All published revisions were ordinary prompt text. Inspected S2 commands read
archived evidence or constructed proposals; no live game/inference probes,
controller changes, button schedules or success overrides were observed. The
reviewers made no tool calls. Two boundary events are retained explicitly:

1. Reflection 6 tried writing its proposal to `/run`, which is read-only. The
   filesystem rejected it with errno 30. The valid proposal was subsequently
   returned normally. Other `/tmp` proposal writes were allowed scratch work.
2. Reflection 24 changed `left_jump` from “another jump” to “a new jump” in its
   answer. Exact equality rejected this before publication. Its retry preserved
   all descriptions. This is distinct from the earlier false reviewer rejection.

Reflection 21 timed out once and succeeded on retry. Both reflection 25 turns
timed out; its retry exhausted the remaining aggregate budget, with no v25
publication. Raw logs and rejected answers are preserved, not discarded.

## Wall time and latency

Original deadline: **2026-09-30 01:39:13.203 UTC**, one hour after launch.
The initial segment occupied 326.60 seconds; repair/restart occupied about 81.55
seconds. The corrected segment inherited **3,191 seconds and at most 47 attempts**.
It ended after 25 attempts; the time limit, not the attempt limit, was binding.

| Corrected-segment activity | Wall seconds |
| --- | ---: |
| S2 proposal turns, including incomplete/rejected turns (28) | 2,850.65 |
| Independent publication reviews (24) | 263.89 |
| Gameplay attempts (25) | 72.72 |
| Other loop/startup/cleanup overhead | 5.10 |
| Recorded terminal elapsed time | 3,192.36 |

S2 and review consumed **51.91 minutes**, about 97.6% of this segment. Gameplay
produced 149.95 native game seconds in 72.72 wall seconds. These are aggregate
lockstep timings, not a real-time 60 Hz performance claim.

| Request class | Count | p50 | p95 |
| --- | ---: | ---: | ---: |
| Encoder work reported | 2,160 | 27.07 ms | 33.34 ms |
| Fully cached (`input_tokens == 0`) | 256 | 2.02 ms | 2.47 ms |
| All requests | 2,416 | 26.50 ms | 33.14 ms |

Encoder work may encode a state, a candidate description, or both; it is not a
pure GPU-kernel measurement. Identical cached states and repeated deterministic
trajectories are not independent generalization evidence. Prompt revisions make
this an adaptive sequence, not 25 repetitions of one fixed policy.

The runner records final **`infra_error` / `TimeoutError('Codex turn stopped/deadline')`**
and systemd exit 1 because the global deadline interrupted an S2 retry. This
report classifies the cause as **budget expiration during reflection**, while
preserving the raw error. Terminal cleanup was approximately **0.50 seconds**
after the original deadline; no further attempt was started. The runner's error
label should be distinguished from an unexplained infrastructure failure. We did
not alter the frozen runtime or extend the budget to change that label.

See [wall-time intervals](evidence/wall-time.json) and [metrics](evidence/metrics.json).

## Verification, provenance and archived replay

- [Native replay](evidence/final.json): all 25 attempts, 2,416 decisions, 8,997 frames; no errors.
- [Input integrity](evidence/single-prompt-integrity.json): exact immutable instructions per attempt, all eight descriptions fixed, no note objects or note clock.
- [Action authority](evidence/action-authority.json): 171 declared A releases, zero other overrides.
- [Source provenance](evidence/source-provenance.json): all 21 deployed/frozen runtime hashes match the checkout runtime after `b308feb`. This does not replace the historical 1-1 initial-import or fixed 1-2 `f78f6d0` source claims.
- [Best video verification](evidence/best-video.json): attempt 16, all 980 native frames checked against RAM; 16.33 seconds at 60 fps.

The full corrected archive is preserved on B200 at
`/raid/juc049/clm-mario/stage12-single-prompt/experiments/reflection-reviewfix/`
and locally under ignored
`deliverables/clm-stage12-single-prompt/reflection-reviewfix/`.
The local video is `audit/best-attempt-0016.mp4` within that archive. Exact model
requests, returned probabilities, chosen/executed buttons and screenshots are in
`attempts/`; full S2 command logs are in `reflections/`. The interrupted segment
remains in the sibling `reflection50/` archive.

The final native replay used the run's own `frozen/` directory as `PYTHONPATH`.
The existing `verify_inputs.py`, `summarize.py` and `audit_action_authority.py`
were run after termination; the best video was replayed without model calls.
The reviewer-fix code already passed 89 tests and lint; completion adds reports
and evidence only. Raw recordings, ROMs, credentials and weights are outside Git.
The public website was not updated. No new experiment was launched.
