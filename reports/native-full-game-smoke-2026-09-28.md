# Native full-game environment smoke test

The new native environment starts at 1-1 with timer 400 and advances one ROM frame per step. It disables the upstream animation-timer writes and hidden post-step frame advances. Boot uses 171 recorded START/release frames, without RAM edits. Boot frames are reported separately from gameplay frames.

Two live DJev attempts ran on AMD using the existing local endpoint on port 18515, in `/home/juc049/projects/mario-amd/native-full-game`. Profiles were frozen before the first attempt; defaults select earlier successful campaign/stage profiles. No prompt changes were made between these two attempts.

| Attempt | Outcome | Furthest stage | x | Timer at death | Decisions | Native frames |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | death | 1-1 | 1127 | 374 | 136 | 530 |
| 2 | death | 1-1 | 1127 | 374 | 136 | 530 |

Both attempts started at timer 400 with the original life/score/power state. They demonstrate full reset on death, not a stage transition or full-game success. Removing the old startup/animation shortcuts changes timing, so earlier stage winners must be revalidated in this environment.

Both trajectories replayed exactly on AMD, matching recorded game information and RAM hashes after every action, with per-frame timer/life/stage checks. Raw traces, full request diagnostics, frozen profiles and source snapshot are preserved in `runs/native-smoke-20260928` on AMD and downloaded to the PR checkout's ignored `runs/full-game/native-smoke-20260928` folder. They are not part of the earlier published campaign or its videos.

Local tests additionally compare 240 native steps against direct raw-emulator steps, verify death/reset behavior, test ordered stage-credit accounting and warp rejection, and reject a tampered replay hash. Stage-transition bookkeeping is unit-tested, but no live transition reached the next stage in this smoke test. A live 1-1 → 1-2 transition and a complete 32-stage run remain to be demonstrated.

Inference pauses the emulator. These are native game-clock measurements, not real-time agent performance.
