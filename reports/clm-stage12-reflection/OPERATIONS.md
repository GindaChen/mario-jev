# World 1-2 with prompt-only reflection

This experiment is in progress; this file records its launch and one infrastructure
repair, not a completed result. It starts from the exact prompt used by the
[failed fixed-prompt pilot](../clm-stage12-single-prompt/README.md). S2 may revise
only the instructions between failed attempts. The eight candidate descriptions,
observation code and gameplay controller remain fixed. Coordinate hints are
allowed as prompt text; host-side note activation and forced actions are not.

## Runs and aggregate budget

All remote paths below are beneath
`/raid/juc049/clm-mario/stage12-single-prompt/` on B200.

| Segment | State at launch handoff | Bounds |
| --- | --- | --- |
| `experiments/reflection50` | Stopped for reviewer repair after 3 failed attempts | Originally 50 attempts / 3,600 seconds |
| `experiments/reflection-reviewfix` | Active, fresh start from the same initial prompt | 47 attempts / 3,191 remaining seconds |

The second segment does not reset the aggregate budget. The authoritative original
deadline is `reflection50/manifest.json`'s `created_unix + wall_limit_s`.
S2 uses `gpt-6-sol` with medium reasoning, with 180 seconds for a proposal and
90 seconds for its independent review. Game steps wait for CLM; reflection runs
between failed attempts. A clear retains its prompt for subsequent attempts.
Poor gameplay is handled by S2, not by an operator writing a solution.

The active systemd user unit is `clm-stage12-reflection-reviewfix.service`.
Read its status plus `experiments/reflection-reviewfix/observations/status.json`
and `events.jsonl`. Exact S2 requests, commands, replies and reviewer verdicts are
under `reflections/`; published prompts and provenance are under `programs/`.
The status snapshot's elapsed time can be stale while S2 works; use the manifest
creation time and event timestamps for live wall-time accounting.

## Reviewer repair

The initial segment's reviewer rejected a candidate claiming its action
descriptions had changed. They were byte-for-byte equal to the experiment's
frozen criteria and had already passed the equality validator. The reviewer had
only been shown generic `DEFAULT_CRITERIA` as its reference. Those generic
descriptions differ from the previously optimized frozen descriptions.

Commit `b308feb` supplies the actual frozen descriptions and explains that equality
has already been checked. It does not weaken validation or change game actions.
A regression test now uses non-default frozen descriptions through the full
mocked proposal/review/publication path; the complete suite passes 89 tests.

The affected segment is preserved. All three attempts died at x=198; its
[replay audit](evidence/initial-segment-replay.json) passes all 60 decisions /
222 native frames. Its `infra_error` terminal status reflects the operator's
SIGTERM during reflection for this repair, not an unreported gameplay outcome.
The [restart record](evidence/restart-reason.json) preserves the aggregate budget.
Do not silently combine the two segments into one homogeneous experiment.

## Completion checks

The in-chat follow-up checks this bounded run every five minutes. At completion,
use the run's `frozen/` directory as `PYTHONPATH` for
`python -m mario_jev.rsi_runtime.audit_clm`. The control root also contains
`verify_inputs.py`, `summarize.py`, `audit_action_authority.py` and
`export_native_video.py`. Verify every completed attempt, immutable per-attempt
prompts, frozen candidates, model-selected versus executed keys and S2 tool use.
Export the first clear or best failed replay, report the outcome and pause the
follow-up. Do not extend the budget or publish the website automatically.

Raw run copies belong in ignored `deliverables/clm-stage12-single-prompt/`.
Commit only compact, credential-free evidence and final prompts/results.
