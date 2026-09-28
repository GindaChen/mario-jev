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

## Next evaluation: restart the whole game on death

The strict mode is **not implemented by this PR**. It should start one full-game environment at 1-1, preserve state at natural transitions, freeze the prompts before evaluation, and restart at 1-1 on any death. Record whole-run success rate, lives/deaths, furthest stage and frame/latency costs across independent runs. Full reset on death demonstrates a deathless run; a conventional game completion that permits losing lives is a different evaluation.

Keep stage/checkpoint retries as a development mode to diagnose late-stage failures cheaply. Use full resets for final evaluation so saved-state successes cannot be mistaken for full-game competence. Any prompt revision starts a new evaluation version rather than silently changing the policy mid-run.
