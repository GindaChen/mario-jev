# Stage-by-stage campaign: an intermediate milestone

This PR adds a DJev reflection controller, ordered campaign runner, deterministic replay/audit tools, frozen stage prompts, and the Game Lab website under `web/`.

The recorded campaign cleared 1-1 through 8-4 in order across **62 stage attempts**, with **30 retries/restarts**. It loaded stages separately after an early failure. This is **not an uninterrupted full-game clear**: lives and power state were not carried across those stage loads. Inference pauses emulator time. The short video stitches the successful attempts; the chronological video includes failures and resets. Replay verification checked all 22,793 recorded decisions.

- 32 clears, 27 gameplay failures, two API errors, one worker restart.
- Stage prompts were prepared in earlier independent-stage research. Successful campaign revisions refined the requests for 2-1, 6-2 and 7-2; 1-1 used reduced context.
- No weight updates. Reflection is supervised prompt refinement between attempts, with stage-specific instruction retrieval and a preexisting jump-release helper.
- The final 8-4 completion uses its axe flag. A guard avoids the stock emulator's final-cutscene hang without writing RAM or selecting gameplay actions.

## Run and inspect

```sh
uv sync --locked
# Requires a running DJev /v1/systemone endpoint; override --endpoints for your hosts.
.venv/bin/python scripts/run_campaign.py --root runs/my-campaign
# Replay without new model calls; --video needs ffmpeg on PATH.
.venv/bin/python scripts/replay_campaign.py runs/my-campaign/trajectory.jsonl
.venv/bin/python scripts/audit_campaign.py runs/my-campaign
```

Use a new output directory for a new campaign. `--resume` preserves its ledger and explicitly restarts the current stage. Inspect `--help` for endpoint and retry settings. After repeated failures the worker waits for a revised per-stage override or a supervisor's continue command; it does not invoke a stronger model by itself.

The website source, read-only publishers and deployment documentation are in `web/`. `web/build_campaign_research.py --campaign-root PATH` rebuilds the frozen 62-attempt research view and validates it against the completed audit. It is a builder for this published campaign, not a general live optimizer. Videos and raw datasets remain external artifacts rather than Git payloads.

Published evidence: https://game.gindachen.com/mario-speedrun/ — includes complete attempts, the stitched compilation, prompt diffs and the audit archive. Earlier independent-stage work is separate: https://game.gindachen.com/mario/ .

## Native full-game evaluation: restart at 1-1 on death

A separate `NativeFullGameEnv` and `scripts/run_full_game.py` now implement this evaluation. The ordinary full-game ROM boots through START button input into 1-1 with its initial timer at 400. Each step advances exactly one NES frame. The environment disables the upstream post-step shortcuts that overwrite area timers, accelerate deaths and skip cutscenes. Natural stage transitions preserve lives, score, coins and power state; each next stage receives the ROM's normal timer. No stage loaders, save-state checkpoints or gameplay RAM writes are used. The initial controller-only boot sequence is recorded separately; repeated attempts restore that same 1-1 starting state.

```sh
# New directory required; all 32 profiles are frozen before any attempt.
.venv/bin/python scripts/run_full_game.py --root runs/full-game/eval-001 \
  --endpoint http://127.0.0.1:18515 --attempts 10
# No model calls: replay and compare RAM hashes and game info after every action.
.venv/bin/python scripts/run_full_game.py \
  --replay runs/full-game/eval-001/attempt-001/trajectory.jsonl
```

- Any death ends the current attempt. The next attempt starts at 1-1; stage-clear credit never carries across attempts. Extra lives do not count as deaths.
- All 32 stages must occur in order, within one attempt, ending in the native 8-4 end-of-world signal. Unexpected stage transitions invalidate the attempt; warps cannot stand in for missing stages.
- Instructions change only by selecting the pre-frozen profile for the current stage. Defaults use the stage winners, the successful reduced-context 1-1 profile and the successful campaign revisions for 2-1, 6-2 and 7-2. `--overrides DIR` selects revised `W-S.json` files **before** evaluation. Start a new evaluation directory after reflection.
- Only DJev chooses playable actions, with the existing generic jump-release helper. Nonplayable animations receive recorded no-button frames; all these frames count. No hand-coded jump sequence is added.
- Logs include full request diagnostics, frozen profiles/source archive, per-frame stage/timer/life signals, RAM hashes, emulated frame counts and wall time. The ROM timer is not wall time: inference still pauses the simulation. Controller boot frames are separately recorded and excluded from gameplay frame totals.
- `--max-decisions` and `--max-frames` bound an attempt. Limits, errors, warps and a `STOP` file stop the evaluation for inspection; only deaths automatically begin another attempt. Interrupted traces remain incomplete, never successful. There is no checkpoint resume.

This is a **deathless** evaluation. Ordinary full-game play that permits losing lives is a different mode. Implementing the environment does not establish a full-game win; the existing published 32-stage campaign remains the earlier stage-linked result.
