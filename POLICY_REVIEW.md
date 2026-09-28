# World 1 situational-policy experiment — code review

**Current direction:** see [SINGLE_PROMPT_REVIEW.md](SINGLE_PROMPT_REVIEW.md) for the continuous run with one prompt. The independent-stage setup below is retained as earlier development work.

This checkout is isolated from the previous campaign and 1-3 experiments. Its branch is `situational-world1`, based on the controller in draft PR #2. The new scope is independent evaluations of 1-1, 1-2 and 1-3, not a continuous three-stage run. New live trials have not started; the code and policies are ready for review.

## Read the code in this order

1. `src/mario_jev/situational.py`: `observation` whitelists relative geometry and movement measurements. `SituationalDjevPolicy.choose` sends one question and a fixed nine-action menu, accepts the model choice, then applies only the approved jump-release helper. Both the selected and executed actions are logged.
2. `prompts/situational/world1/`: exact versioned requests for all three stages. General mechanics are shared; stage guidance differs. No coordinate ranges, timed notes, action-menu overrides or room-based routing. The 1-3 profile retains the measured platform-tile perception extension.
3. `src/mario_jev/cli.py`: dispatches `mode: situational` to the new controller. Old controller modes remain available.
4. `scripts/run_situational_world1.py`: freezes all selected profiles, then schedules bounded per-stage batches in separate directories. Default is three attempts per stage, nine total, sequentially on one DJev endpoint. Prepare-only mode makes no inference calls. Each batch records source/profile snapshots and full decision traces using the existing runner.
5. `tests/test_situational.py`: verifies absolute-position invariance, fixed action choices, faithful action execution except the approved jump release, and rejection of routing overrides.

## Important boundaries

The existing stage loader and animation shortcuts are still used for these independent development trials. They do not validate native full-game timing. Perception is approximate and uses RAM-derived relative geometry. The model receives the stage label but no absolute coordinates, room IDs or note clocks. Audit logs retain absolute positions for failure analysis. Fixed four-frame action holds are execution granularity; the jump-release helper may use one frame.

Previous 1-3 evidence belongs to PR #2: six trials, zero clears. The new world-1 profiles are not established winners. Changes to guidance should become new versions and new result directories, never edits to a completed trial's snapshot.

## Reproduce preparation or launch after review

```sh
uv sync --locked
# Freeze all three profiles; no model calls.
.venv/bin/python scripts/run_situational_world1.py --root runs/world1-review --prepare-only
# Use a DIFFERENT new directory when launching on the inference host.
.venv/bin/python scripts/run_situational_world1.py --root runs/world1-v1 --repeats 3 --endpoint http://127.0.0.1:18515
```

A `finished` batch means its worker completed, not that Mario won. Read each trajectory's `completed` field for success. A runner interruption leaves its plan incomplete; this launcher does not resume or overwrite an existing root.
