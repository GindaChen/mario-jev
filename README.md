# Mario + Jev

A uv-managed Python prototype that plays NES Super Mario Bros. (level 1-1 by default).
Jev receives structured RAM observations and answers focused questions about movement, starting a jump, and sustaining
a jump, plus timing hops under low ceilings. Code composes their answers into controller buttons.
The emulator pauses while Jev responds, then advances up to four game frames by default, stopping early on landing.
The resizable game window opens at 800×600 by default. No JavaScript is required.

## Setup

```sh
uv sync --locked
cp .env.example .env
```

Put your TypeSafe key in `.env`:

```dotenv
TYPESAFE_API_KEY=your-key-here
```

The key can also be supplied through your shell environment. `.env` and `runs/`
are ignored by Git. Do not put API keys in gameplay logs or commit them.
Python 3.13 is selected by `.python-version`; uv installs it if needed.

## Play

Try the emulator without API calls:

```sh
uv run mario-jev --policy scripted
```

Make a short Jev run first (at most 25 API requests):

```sh
uv run mario-jev --decisions 25
```

Then run a longer attempt:

```sh
uv run mario-jev --decisions 500
```

Choose a world (1–8) and stage (1–4):

```sh
# Next level: 1-2
uv run mario-jev --world 1 --stage 2 --decisions 500

# World 2, stage 1
uv run mario-jev --world 2 --stage 1
```

Both options default to 1. Replay uses the level saved in the log.

Additional commands:

```sh
# Inspect exactly what Jev will see, without calling it
uv run mario-jev --dump-state --headless

# Run the baseline without a game window
uv run mario-jev --policy scripted --headless --episodes 3

# Tune the time each action is held
uv run mario-jev --frames 4 --decisions 200 --model jev-latest

uv run mario-jev --help
```

Each episode resets the selected level, and ends on death, completion, or the decision
limit. Ctrl-C stops the run. Jev calls use a 15-second HTTP timeout with automatic
retries disabled; an API error stops gameplay instead of consuming more requests.
Every Jev decision is a paid API request. `--decisions` limits calls per episode;
`--episodes` multiplies that limit. No API key is needed for the scripted policy
or state dump.

## Self-hosted DJev

This checkout also supports `--policy djev`. It sends the original four questions
and RAM observations to DJev's `/v1/request`, using the same button composition
and 0.5 jump thresholds. Questions are evaluated independently by default, using
four model reads per decision. Use `--djev-isolation joint` to reproduce the
original one-read configuration. The selected mode is recorded in each run's
configuration, and backend diagnostics record physical reads.

No TypeSafe API key is used or forwarded. Start a
[DJev server](https://github.com/Davipar/djev-dev) first. For a remote server
listening on port 18341, replace `YOUR_GPU_HOST` with your SSH host:

```bash
ssh -N -L 127.0.0.1:18341:127.0.0.1:18341 YOUR_GPU_HOST
```

In another terminal, run a bounded game:

```bash
uv run mario-jev --policy djev --decisions 50
```

Add `--log-every 10` to print terminal progress every 10 decisions, starting at
decision 0. The default is 25; use `--log-every 1` to print every decision.
JSONL trace files always retain every decision.

Use `--djev-url http://127.0.0.1:PORT` for another API root. Requests use one
diffusion sample, seed 0, a 60-second timeout, and no retries. Logs retain DJev
diagnostics, including its unvalidated probability calibration. A failed request
stops the game; it never falls back to the hosted Jev API.

In a September 26, 2026 comparison on world 1-1, seed 123, with a 500-decision
limit and the original prompts and button rules:

| Backend | Decisions | Furthest x | Outcome |
| --- | ---: | ---: | --- |
| DJev, joint questions | 27 | 315 | Died at the first Goomba |
| DJev, independent questions | 362 | 3161 | Completed |
| Jev reference run | 351 | 3161 | Completed |

DJev used the BF16 B200 runtime at `Davipar/djev-dev` revision `3ce907e`.
These are individual runs, not measured success rates. Independent mode uses
four physical model reads per decision instead of one. DJev's request adapter
does not make its model judgments or probability calibration equivalent to Jev's.

## Replay

Replay a recorded gameplay log with no API calls or API key:

```sh
uv run mario-jev --replay runs/20260917T051444816158Z.jsonl

# Twice normal playback speed
uv run mario-jev --replay runs/20260917T051444816158Z.jsonl --speed 2

# Fast headless verification
uv run mario-jev --replay runs/20260917T051444816158Z.jsonl --headless
```

Substitute your own timestamped log path. Playback uses the recorded seed,
controller actions, and actual frames executed, including landing-shortened
intervals. It checks positions against the log and stops on divergence. Keep
`uv.lock` and the same game/emulator version for reproducible playback. Visible
playback defaults to normal game speed because there is no model wait. Logs are
local and excluded from Git; the sample filename refers to the verified local
successful run, not a bundled recording.

## Observations and logs

`state.py` decodes Mario's position, motion, grounded state, nearby enemy slots,
and the visible portion of the two RAM metatile buffers. It adds measured Mario
and enemy velocity in pixels per game frame, approximate time to enemy contact,
body/feet coordinates, nearby obstacle height, empty terrain columns, overhead
clearance, blocked-forward detection, and the last twelve transitions by default. A jump corridor reports
ceiling spans up to 128 pixels ahead, available headroom, and whether low bricks
lie on the approach to an enemy. This is geometry rather than jump simulation. Velocity is
an average over the previous action interval; it is not a predicted trajectory.
Enemy estimates reset when the slot/type changes or a teleport is detected.

Tile columns are relative to Mario, with thirteen rows starting at screen y=32.
The decoder uses a small set of known vanilla SMB1 solid tiles; raw metatile IDs
remain available. Unreported terrain is unknown. It is specific to vanilla SMB1,
not SMB2, SMB3, or ROM hacks. Empty columns can indicate pits or drops; geometric
summaries and contact times are approximate, not collision guarantees.

Each transition includes before/after position, measured velocity, grounded state,
action, actual frames held, reward, and possible landing/head-bump/blocking events.
`current_jump` tracks takeoff, elapsed frames, distance and peak height across the
whole jump, even when takeoff leaves the recent-history window. `last_jump`
reports the previous completed jump. The last four consecutive frame samples are also included as `recent_frames`.
Memory resets at each episode. Velocities
are interval averages; collision events are estimates, not engine guarantees.

The runner checks RAM after every emulator step. It interrupts frame repetition
on landing and immediately asks Jev for the next action, recording the actual
frames held and `landing_frame`. Four is the maximum default action duration,
not a promise to always hold buttons for four frames. This avoids hiding a
brief grounded state between calls. It borrows the four-frame action interval
and observation history from the prior PPO pipeline, while landing interruption
is an additional safeguard for the API controller. Compared with six-frame
actions, four-frame actions need roughly 50% more calls per game second; landing
interruptions can add more.

`landing_surfaces` describes exposed solid tile tops and visible floor gaps,
including a far-bank height where available. These are candidates, not guaranteed
reachable surfaces. History and geometry help Jev reason about trajectories;
there is no forward physics simulation yet. `--history 8` changes the recent
transition count. More history increases input-token cost, not requests per decision.

Jev answers `movement` (run/walk/brake/wait), `start_jump`, `ceiling_hop`, and
`sustain_jump` in one API call. Jump answers use Noul probabilities with a 0.5
threshold. On an enemy approach under low bricks, without a competing pipe or
pit, code uses the focused `ceiling_hop` answer instead of the ordinary
`start_jump` answer.
Code selects start-jump only when grounded and A previously released, and uses
sustain-jump while airborne. It adds no scripted hazard override. Separate jump
buttons allow braking or waiting while jumping. Logs record every model answer
and the composed action; the reported top-level confidence belongs to movement,
not to the complete controller action or probability of surviving.

Timestamped `runs/*.jsonl` files contain configuration, input state, controller
choice, Jev confidence and probabilities, token usage, API latency, actual frames
executed, reward, next position, and episode summaries. These are decision logs,
not saved emulator states or video recordings. The composed controller action is executed directly.

The scripted controller is a simple baseline. Local verification reached x=2471
before dying; it does not currently complete the level. A bounded live evaluation of the revised Jev controller passed the first Goomba,
early pipes, and first pit, reaching x=1594 after 110 decisions without dying.
The original controller died at x=315. These are individual runs, not a measured
completion rate; full-level completion is not yet demonstrated. A targeted replay of a later
ceiling/Goomba failure reached x=2902 alive with the ceiling timing improvement;
the original recorded run died at x=2764. The replay restores the approach by
executing recorded actions, then uses fresh Jev decisions. It is not a full run
or training. With richer transition history and landing geometry, a replay of the
later ditch approach landed on the upper stair, launched a second jump, and
reached x=2567 alive beyond the gap; the previous runs died around x=2472–2474.
With four-frame actions and per-frame landing interruption, another replay
caught the upper-step landing at x=2431 after one frame, launched a new jump,
and reached x=2551 alive.

## Development

```sh
uv run pytest
uv run ruff check src tests
uv run ruff format --check src tests
```

- `src/mario_jev/cli.py`: episode runner and JSONL logging
- `src/mario_jev/state.py`: SMB1 memory decoding and terrain geometry
- `src/mario_jev/history.py`: bounded transition history and jump tracking
- `src/mario_jev/runner.py`: per-frame observations and landing interruptions
- `src/mario_jev/policy.py`: Jev choices, button mappings, and scripted baseline
- `uv.lock`: exact resolved dependency versions

References: [TypeSafe SDK quick start](https://docs.typesafe.ai/introduction/quickstart),
[gym-super-mario-bros](https://github.com/Kautenja/gym-super-mario-bros),
[SMB1 memory definitions](https://github.com/threecreepio/smb-disassembly/blob/master/src/smb.asm).
The installed emulator package supplies its game assets; this repository does
not copy or distribute ROM files.

## Other decision models

The `scorer` policy supports `laya`, `kev`, `nimble`, `openjev4`, and
`openjev35` through the decision-model HTTP scorer gateway. It sends the same
RAM observation and four question instructions as Jev, evaluates each question
independently, and reuses the original button logic. Movement options retain
both their IDs and descriptions. Jump questions use binary `false`/`true`
candidates; the score for `true` uses the existing 0.5 threshold. These scores
are **not assumed to have Jev's Noul calibration**. No TypeSafe key is needed
or sent to the scorer.

```sh
# Terminal 1: tunnel to your scorer gateway
ssh -N -L 18797:127.0.0.1:8797 YOUR_GPU_HOST

# Terminal 2: choose a model
uv run mario-jev --policy scorer --model kev --headless \
  --decisions 500 --log-every 25 --log-dir runs/kev
```

Use `--scorer-url URL` to change the gateway. A standalone worker serving
`POST /score` instead of `POST /score/{model}` also needs `--scorer-direct`.
Every trace contains all four exact request payloads, returned candidate
probabilities, token counts, controller decisions, and RAM observations.
Replay any trace with `--replay PATH`; no inference is needed.

The first comparison uses the existing B200 checkpoints: Laya 421M
(`convaiinnovations/laya`), Kev **0.5B**, Bespoke-Nimble-9B, and OpenJev
Qwen3.5 4B v5 / 35B-A3B NLI. This does not test Kev-9B,
Laya-typed-decisions, or full-generation DiffusionGemma. Model revisions are in
`reports/scorer-provenance.json`.

Laya's short default question budget would truncate these instructions. The
Laya requires `--scorer-direct --scorer-url http://127.0.0.1:18821`
with a tunnel to its separate worker on container port 8821. The
isolated `serving/reference_worker.py` runs within the existing
`decision-models-b200` runtime, expands the context to 8192 and question budget
to 2048 tokens, and rejects truncation. It does not change the existing Laya
service. Context extension is an experimental setting, not a claim about
long-context accuracy. The other reference workers reject oversized inputs.
All of these are candidate scorers, not autoregressive text generators.

See [the five-model Mario comparison](reports/other-models.md) for results, limits, and replay paths.

## Winning Laya controller and failure retries

Laya now has a native policy with a frozen prompt profile that completed World
1-1 in three fresh runs (308 decisions each). See the
[experiment and integrity report](reports/laya-success.md) for the exact division
between model decisions, human-written physics guidance, and button mechanics.
The base checkpoint weights and game are unchanged.

With the native Laya worker/tunnel available on port 18821:

```sh
uv run mario-jev --policy laya --headless
```

Use `--laya-profile prompts/laya/v9.json` to select the winning profile explicitly,
or pass another profile to test a prompt change. Every failed/stalled run writes
an adjacent `.failure.json`. Retry before a failure with:

```sh
uv run mario-jev --policy laya --headless --resume runs/FAILED_TRACE.jsonl \
  --rewind-frames 300 --laya-profile prompts/laya/v9.json
```

The prefix is reconstructed from recorded actions and verified before new model
calls. Resumed completions are marked separately from fresh passes. The default
stall limit is 100 new decisions without increasing furthest x; change it with
`--stall-decisions`. A replay can also be exported to video with
`python scripts/export_replay.py TRACE.jsonl OUTPUT.mp4` (requires ffmpeg).
