# Overnight campaign

Authorized goal: run from1-1 through8-4 with DJev; stage or checkpoint restarts are allowed. Keep the live website truthful about those restarts. Do not count old independent wins as new campaign clears.

- AMD harness: `/home/juc049/projects/mario-amd/harness`.
- Worker: user systemd `mario-campaign.service`; script `scripts/run_campaign.py`.
- Live files: `runs/overnight-campaign/status.json`, `trajectory.jsonl`, `latest-frame.jpg`, immutable `profiles/`, `sources/`.
- Public progress: https://game.gindachen.com/mario-speedrun/ ; safe projection `/data/campaign.json`.
- Website source/deployment: local sibling `game-lab-campaign/campaign-contract.md`, remote `/home/juc049/projects/game-lab`; separate `game-lab-campaign.service` publisher.
- Supervisor heartbeat: Codex automation `mario-overnight-campaign`, every10minutes in this chat; inspect/fix failures rather than endlessly repeat them.

## Runner behavior

Starts full-game SuperMarioBros-v0, observes natural stage transitions, switches stage profiles. Death/stall can reset only the current stage using its targeted environment; mode then explicitly becomes stage_linked. Environment restarts remain in the append-only trace and public counters. After each5failures it reports needs_reflection. Write an updated `overrides/W-S.json` or a `continue.json` control file after inspecting failures. Ordinary profile updates are read on the next attempt and do not require restarting the service. Code changes do require an explicit service restart; --resume preserves the ledger and records an additional stage reset. Avoid interrupting healthy current-stage progress unnecessarily.

A source snapshot is taken each process start. Both infrastructure errors and gameplay failures remain visible. There are no scripted gameplay action overrides; Jev chooses actions, with the preexisting jump-release helper. Cutscene waits are labeled separately. The stock environment already skips nonplayable transitions; this is not a real-time speedrun benchmark. A final-cutscene guard avoids the upstream8-4 infinite skip and does not modify RAM or controls.

## Verification

`scripts/replay_campaign.py runs/overnight-campaign/trajectory.jsonl` reconstructs every environment reset, executes recorded actions, verifies exact post-step x/y/world/stage/completion, and checks all32clear events. `--allow-incomplete` audits prefixes only. `--video runs/overnight-campaign/campaign-replay.mp4` renders the complete recorded run including failed attempts and labeled reset boundaries.

Final publication requires status completed plus32clears and a published verification wrapper with `{campaign_id: exact ID, replay_verified: true, completed: true}`. Publish MP4+verification under game-lab/public/data/campaign-final/<safe-slug>/ and set status.artifacts.replay_url and verification_url to the corresponding public URLs. See website contract. Do not publish partial replay as completion. Pause the heartbeat after successful verified delivery.

## Early findings

1-1 current default full observation exceeded the4k context; minimal observation fixed inference. That profile cleared1-1 on attempt5. 1-3 initially repeated a model-choice divergence at decision126 with identical state/request to the historical winner, but cleared before the planned focused-grounded override was needed. World1 completed. 2-1 repeated a divergence at decision174: rising should choose left_jump, but chose right_run amid the long global prompt. Campaign override2-1-r01 replaces that local instruction and projects only motion. Exact observations/requests remain in the trace.

## Completed outcome

The new campaign cleared all 32 stages in order at 2026-09-28T08:24:25Z. There were 62 attempts: 32 successful, 27 gameplay failures, 2 API errors, 1 worker restart. All world 8 stages except 8-4 cleared first attempt; 8-4 cleared attempt 5 with original r82. Targeted successful campaign revisions were 2-1 r01, 6-2 r02, and 7-2 r01 plus minimal context for 1-1. Unused candidate prompts remain labeled in reports. Final trace contains 22,793 decisions; a one-decision periodic-status lag was reconciled while preserving original status.

Final downloadable evidence resides under runs/overnight-campaign and the website's campaign-final folder. The run is stage-linked with explicit resets and inference pauses. It is not an uninterrupted speedrun.
