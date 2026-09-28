# Continuous 1-1 → 1-3: one prompt

This is the current experiment design. The earlier independent-stage launcher and profiles remain available, but are not used by this command. New live inference trials have not started.

## Exact instruction text — identical on every request

Choose the controller action that makes safe progress toward the goal on the right. Infer the current situation from relative geometry and motion. Plan a landing, not just a takeoff: the feet must reach the top of a supported surface before descending below it. Running builds horizontal momentum; left can brake it. Holding jump while rising can increase height; pressing jump after falling cannot rescue a missed takeoff. Release jump before starting another jump. Compare current velocity, remaining platform length, target height, headroom and nearby enemies. Candidate surfaces are observations, not guarantees of reachability or safety. Empty floor underneath a platform does not mean the platform is absent. Unknown offscreen terrain is not confirmed support. Choose from the same action menu in every situation. Account for low ceilings shortening a jump and for enemies occupying a landing. Approach pipes with enough room to clear their tops. Choose supported intermediate landings on stairs or elevated platforms when one jump would be unsafe. Use the ordinary route toward the end of each stage; do not seek shortcuts that skip stages.

The fixed menu is: wait, right, right_jump, right_run, right_run_jump, left, left_jump, jump, down. Its descriptions state only which buttons are held. `src/mario_jev/situational.py` contains the exact descriptions and measured-observation whitelist.

## What changes during play

Relative geometry, motion, enemies, power state and jump-held state change as the game evolves. This profile does not send a stage label, absolute coordinates, room identifiers, stage guidance or note timers. The same instruction text and action criteria go into every model request. There is one model call per playable decision, not one model call for the entire game.

`freeze_single_profile` in `scripts/run_full_game.py` freezes one file and records the same hash for every stage. The policy instance remains alive across stage transitions. Short observation history is reset at the transition to avoid interpreting a new level's coordinates as physical movement. This does not replace the prompt. Profiles are only read again for integrity checking; no instruction edits occur during a run.

## Environment and success condition

One native emulator starts at 1-1 with timer 400. It preserves normal cutscenes, next-stage timers, score, lives and power state. Clearing 1-1, 1-2 and 1-3 in order and reaching playable 1-4 ends this partial evaluation before another action. A warp invalidates the ordered run. Death ends the attempt; another attempt restarts at 1-1. This is a deathless three-stage evaluation, not all of World 1 or a full-game clear.

The approved generic jump-release helper remains. Its selected and executed actions are separately recorded. Nonplayable animations receive recorded no-button frames. No gameplay RAM writes, stage reloads, coordinate routing or timed maneuver sequences are added. The platform perception extension is fixed for the whole run. Inference pauses simulation, so this is not real-time agent play.

## Run after code/prompt review

```sh
.venv/bin/python scripts/run_full_game.py \
  --single-profile prompts/situational/continuous/v1.json \
  --through 1-3 --attempts 3 --frames 4 \
  --root runs/continuous-single-v1 \
  --endpoint http://127.0.0.1:18515
```

Run this on the inference host or supply a reachable endpoint. Use a fresh output folder. To check a recorded attempt without new inference:

```sh
.venv/bin/python scripts/run_full_game.py \
  --replay runs/continuous-single-v1/attempt-001/trajectory.jsonl
```

Tests cover a shared frozen profile, fixed action menu, faithful execution with the approved exception, ordered partial-run completion, native stepping and replay validation. They do not establish that this prompt can clear the three stages. No new live success is claimed.
