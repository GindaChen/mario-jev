# Laya passes Mario World 1-1

2026-09-27. Same Laya 421M checkpoint as the failed baseline; B200 inference.

**Three fresh runs reached the flag: 308 decisions, maximum x=3161 each.**
The final run used seed 123, four frames per action, and the ordinary 500-decision
limit. It had no replayed prefix. This is repeated execution of one deterministic
level/configuration, not an estimate of success on unseen levels.

## What changed

The previous generic scorer made the same four choices on all 168 decisions.
The new `--policy laya` uses the native Laya API and short, separate questions:

- Laya selects horizontal movement from the visible scene.
- On the ground, Laya separately selects absent/far/near timing cases for enemies,
  walls, and pits. General spacing guidance is written in the prompt. Code does
  not compare a distance with a jump threshold to select an action.
- While airborne, Laya selects rising/hold versus falling/release. Code maps its
  selected case to the jump button.

Distances are expressed as approximate **Mario body lengths** (16 pixels), with
correct singular/plural wording. The closest measurement is described as
"within one body length"; larger distances are rounded and explicitly marked
"about". General prompt guidance uses three body lengths for ordinary approaches
and two for enemies under a low ceiling. Those are human-authored physics rules,
not learned strategy or level-specific coordinates.

This is a **model-executed, prompt-programmed reactive controller**. Laya selects
cases; ordinary code combines those selections into buttons. It is not a claim
that the base model independently discovered a strategy or performs long-horizon
planning. Neutral label IDs A/B/C reduce distracting action-word associations.

## Integrity of the pass

The emulator, ROM, collision rules, health, reward, and flag condition were not
modified. There is no emulator lookahead, prerecorded winning action sequence,
absolute-level-coordinate action rule, or foreign model choosing live actions.
The checkpoint weights were not trained or changed. The observation still uses
RAM-derived geometry, as the original Mario-Jev harness does.

During the canonical 308-decision run, there were 814 native Laya requests:
308 movement selections, three hazard selections on each of 99 grounded
observations, and 209 airborne hold/release selections. The airborne outputs
included 125 rising/hold and 84 falling/release choices. Grounded choices included
clear/absent, distant, and close cases. They were not constant outputs.

The mechanical A-rearming guard never overrode a requested jump in the winning
run. Tests also verify that a model vote to continue approaching makes the
controller keep running even at a blocking wall; there is no hidden jump fallback.

Development traces before the canonical run retain an incorrect
configured-model alias inherited from the old CLI default. Their per-decision
model identity is the actual pinned Laya checkpoint. This metadata issue is fixed
in the canonical `final` trace below; raw earlier traces were not edited.

## Development record

| Experiment | Fresh start? | Maximum x | Decisions | Outcome |
|---|---|---:|---:|---|
| Native button prompt v1 | Yes | 682 | 71 | Died |
| Short v2, retry from earlier failure | No | 1130 | 111 total / 23 new | Died at pit |
| Modular pixel-distance v7 | Yes | 315 | 27 | Jumped too early |
| Body-length v8 | Yes | 723 | 166 | Stalled at pipe |
| Corrected wording v9, retry before stall | No | 3161 | 337 total / 246 new | Reached flag; development only |
| Frozen v9, fresh test | Yes | 3161 | 308 | Passed |
| Frozen v9, repeat | Yes | 3161 | 308 | Passed |
| Frozen v9, default CLI / canonical trace | Yes | 3161 | 308 | Passed |

Offline prompt probes are retained under `runs/laya-lab/`; probe-only profiles are
under `runs/laya-lab/prompt-probes/`. The reusable winning profile is
[`prompts/laya/v9.json`](../prompts/laya/v9.json). Playable failed variants remain
alongside it. The machine-readable experiment record is
[`laya-experiments.json`](laya-experiments.json).

## Failure recording and retry

A failed or stalled run writes an adjacent `.failure.json` containing the last
observation, outcome, trace path, and retry parameters. `--resume TRACE`
reconstructs the emulator and observation history by replaying the recorded
buttons, without model calls. It verifies every observation and position in that
prefix before allowing the new prompt to control the game. No RAM is edited.

`--rewind-frames 300` resumes approximately five seconds of 60 Hz gameplay before
the source trace ended, rounding back to an action boundary. A trace shorter than
300 frames restarts at the beginning. The cap given by `--decisions` applies to
new decisions; replayed decisions are explicitly marked and excluded from that
cap. A resumed completion is marked `fresh_start: false` and does not count as a
fresh evaluation. By default, 100 new decisions without increasing furthest x
stop the run as `stalled`.

```sh
uv run mario-jev --policy laya --headless \
  --laya-profile prompts/laya/v9.json \
  --resume runs/laya-lab/v8/20260927T175101516549Z.jsonl \
  --rewind-frames 300 --log-dir runs/laya-retry
```

## Run and inspect

The existing native worker is available through the local tunnel on port 18821.
It extends the prepared `decision-models-b200` worker runtime with `/decide` and
rejects input truncation. `--laya-url` changes the endpoint. The service source is
`serving/reference_worker.py`; it depends on the existing benchmark runtime and
its `worker.py`, Laya package, and model files.

```sh
# Fresh gameplay using the winning default profile
uv run mario-jev --policy laya --headless

# Watch the canonical trace; no model calls
uv run mario-jev --replay runs/laya-lab/final/20260927T175724879937Z.jsonl
```

Canonical trace: `runs/laya-lab/final/20260927T175724879937Z.jsonl`.
Video of the matching first fresh run: `runs/laya-lab/laya-world-1-1.mp4`
(19.72 seconds of gameplay, without inference pauses).

All traces retain exact requests, responses, profile hashes, selected actions,
RAM observations, and game outcomes. The canonical trace was replayed and all
308 positions matched. The MP4 export independently checks positions while
encoding. The test suite has 37 passing tests; lint checks pass.

No new performance claim is made for Nimble, Kev, OpenJev, or other levels.
