# CLM single-prompt Mario experiment

CLM chooses controller actions from the current observed game state and one
instructions string. That string stays fixed throughout an attempt. After a
failed attempt, System 2 can rewrite only the instructions; the eight candidate
descriptions are frozen. There are no runtime memory-note objects, retrieval,
note timers or prompt routers in this mode.

The supplied warm start is the previously optimized v21 instructions plus all
of its global failure-note text, concatenated once. Historical experience stays
in the prompt. This is not a cold-start or experience-free experiment.

## Read the code

| File | Responsibility |
| --- | --- |
| [clm_single_prompt.py](src/mario_jev/rsi_runtime/clm_single_prompt.py) | Entry point, single-prompt schema and immutable candidate descriptions |
| [clm_pilot.py](src/mario_jev/rsi_runtime/clm_pilot.py) | Lockstep game loop, failure reflection, independent review and version publication |
| [clm.py](src/mario_jev/clm.py) | CLM wire adapter; preserves exact prompt text and removes the unused note clock |
| [reflection.py](src/mario_jev/reflection.py) | Existing observation construction and grounded A-release helper; unchanged |
| [clm_support.py](src/mario_jev/rsi_runtime/clm_support.py) | JSON helpers and native-frame environment factory |
| [audit_clm.py](src/mario_jev/rsi_runtime/audit_clm.py) | Exact request, controller, image and full-RAM replay checks |

Start with the [complete S1 prompt](prompts/clm/single-prompt/template/initial-instructions.md)
and [S2 prompt](prompts/clm/single-prompt/template/system2-instructions.md).
The [source program](prompts/clm/single-prompt/source-program.json) contains the
original instructions, candidate descriptions and historical memory text.
Initialization concatenates `instructions + "\n" + memory`. Published programs
have only `instructions` and `criteria`; no memory field remains.

`initial-instructions.md` is a readable copy of the exact combined text. To
change this warm start, edit the source-program input, not just that copy. You
can place all initial text in source `instructions` and leave source `memory`
empty. Runtime prompts are recorded exactly in every decision JSON.

The legacy `clm_pilot.py` and `clm_fixed.py` modes are retained for comparison.
They have different editable fields; use `clm_single_prompt` for this experiment.

## Run the fixed baseline

Install the repository dependencies with Python 3.13+ and `uv sync --locked`.
CLM must be served separately at an endpoint supporting `/v1/systemone` and
`clm-latest`. This repository does not ship model weights, credentials or ROM
files. The [model revisions](prompts/clm/single-prompt/model-revisions.json)
record the encoder and projection-head versions used for the experiment.

Copy the template to a writable control directory outside the checkout:

```sh
clm_control="$(mktemp -d)"
cp -R prompts/clm/single-prompt/. "$clm_control/"
PYTHONPATH="$PWD/src" uv run python -m mario_jev.rsi_runtime.clm_single_prompt \
  --control "$clm_control" --name fixed3 \
  --source-program "$clm_control/source-program.json" \
  --endpoint http://127.0.0.1:18432 \
  --fixed --max-attempts 3 --wall-limit 600
```

This mode never launches S2. Results are saved under
`$clm_control/experiments/fixed3/`; run names cannot overwrite existing runs.
The process exits at the attempt or wall-time limit.

### Try World 1-2

The evaluator selects the starting level with `--world` and `--stage` (default
`1 1`). These are fixed for the run, recorded in its manifest and checked against
the native reset state. Neither S1 nor S2 can change them during an attempt.

```sh
clm_control="$(mktemp -d)"
cp -R prompts/clm/single-prompt-1-2/. "$clm_control/"
PYTHONPATH="$PWD/src" uv run python -m mario_jev.rsi_runtime.clm_single_prompt \
  --control "$clm_control" --name fixed3 \
  --source-program "$clm_control/source-program.json" \
  --world 1 --stage 2 --fixed --max-attempts 3 --wall-limit 600
```

This [1-2 prompt](prompts/clm/single-prompt-1-2/template/initial-instructions.md)
combines the v21 base instructions with four earlier DJev 1-2 lessons. All hints
are ordinary text, present on every decision, including their coordinate ranges.
The old timed plant-wait note is adapted to an untested visible-motion hypothesis
because there is no note clock. This first transfer failed **0/3 clears**, dying
at x=198 after selecting `right_run` on all 20 decisions each time. No S2 ran.
See the [1-2 result and action-authority audit](reports/clm-stage12-single-prompt/README.md).
The subsequent reflection run and reviewer-reference repair are tracked in
[the 1-2 reflection operations record](reports/clm-stage12-reflection/OPERATIONS.md).

## Enable failure-only reflection

Omit `--fixed`, use a new run name and set `--max-attempts 50 --wall-limit 3600`.
The game waits for each CLM response, then pauses between failed attempts while
S2 works. Successful attempts retain the current prompt. Review acceptance
checks integrity, not improvement; there is no performance keep/revert gate.

S2 currently uses the existing Linux/Docker Codex setup: `gpt-6-sol`, medium
reasoning, up to 180 seconds per proposal, and an independent 90-second reviewer.
It requires a compatible Codex binary directory (`CODEX_BIN` in `clm_support.py`),
the `python:3.12-slim` image, the `mario-rsi-agent` Docker network with its
restricted `proxy:8080` egress service, and logged-in `auth/` and
`reviewer-codex/` directories beneath the control root. Those external resources
are not created by this PR. Run it in the existing configured environment or
provide equivalent infrastructure before enabling reflection.

S2 has a read-only experiment mount and root filesystem, a separate writable
workspace, and no emulator or inference socket. Its proposed program is
validated before the independent reviewer is called. Neither agent can publish
code or change the ROM, checkpoint, scoring, action meanings or model weights.

## Fixed controller and evidence

This mode deliberately retains the existing maximum four-frame action duration,
early observation on landing and one-frame A release when grounded with A held
and another jump selected. The helper is not learned. The emulator advances
native frames without upstream post-step death/scene skips. Completion requires
the native flag event.

Conditional stage hints, including coordinate ranges written in the fixed prompt,
are allowed. CLM must interpret them and choose the action. Host-side region
routers, forced jumps at particular positions, recorded button replay and
elapsed-time/frame-index button schedules are disallowed. The 1-2 S2 template and
single-prompt reviewer use this contract; the historical 1-1 template retains its
original, stricter wording. This permission does not enable any code routing.

The shared legacy `reflection.py` still contains optional geographic note
activation and a fallback path for other experiments. Single-prompt profiles
reject all fields that enable those paths. Regression checks test every candidate
at twelve old note boundaries with both legacy paths patched to fail if called.
Observation code can measure geometry; it cannot force a controller action in
this mode. Attempt limits can stop a run, but cannot choose buttons.

The warm-start baseline cleared 3/3, followed by 50/50 with failure reflection
enabled. There were zero failures, zero prompt updates and zero real S2 calls in
the latter run. All 50 trajectories were identical at the same checkpoint and
seed, and all requests hit the cache primed by the baseline. These are
reproducibility results, not 50 independent samples or a generalization estimate.
Each attempt selected `right_jump` 527 times and `right_run_jump` 9 times, with
46 automatic A releases. See the [results and audit report](reports/clm-single-prompt-v21/README.md).

## Checks and replay

```sh
PYTHONPATH="$PWD/src" uv run pytest
uv run ruff check src tests
```

For a new run made from this checkout, replay without inference:

```sh
PYTHONPATH="$PWD/src" uv run python -m mario_jev.rsi_runtime.audit_clm \
  "$clm_control/experiments/fixed3" \
  --output "$clm_control/experiments/fixed3/audit/final.json"
```

The audit intentionally rejects runtime source drift. For an older archived run,
use that run's `frozen/` directory as `PYTHONPATH`, not a later checkout. The
small checked-in evidence files are audit outputs; raw per-decision traces,
screenshots and videos are kept outside Git.
