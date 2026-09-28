# DJev plus System 2 reflection: world 1-2

**World 1-2 passed. The two frozen winning profiles passed 20/20 additional fresh validation runs.** All live gameplay used AMD-local DJev on physical GPU7. No hosted Jev, GPT gameplay API, model training, ROM edits, or replayed action prefixes were used in these 100 attempts. GPT served as the offline experiment analyst and prompt/memory author between batches.

## Results

| Condition | Attempts | Passes | Furthest x |
|---|---:|---:|---:|
| Adaptive discovery, trials 1-60 |60|4|3161 (completed)|
| Frozen r35, 60-frame wait, trials 61-80 subset |10|10|3161 (completed)|
| Frozen r36, 90-frame target wait, trials 61-80 subset |10|10|3161 (completed)|
| Remove only waiting lesson, trials 81-100 subset |10|0|1658|
| Remove all retrieved memory notes, trials 81-100 subset |10|0|980|

Overall: 24 passes in 100 attempts. The 20/20 figure is the frozen validation result, not the success rate of the entire adaptive search. Both winning profiles also passed their two discovery runs. Tests use the same world 1-2/reset seed; they establish repeatability in this scenario, not unseen-level or whole-game ability. Up to 8 experiments ran concurrently against the same GPU7 service.

## What reflection changed

1. Replace independent movement/enemy/wall/pit votes with one model-selected complete action. This prevents a jump vote from contradicting a retreat instruction.
2. Retain grounded support height, recent action, enemy motion, and retrieved stage lessons. Keep the reflection controller active when Mario retreats across its activation point.
3. Present measured distance/geometry facts. DJev chooses the action; code computes facts, retrieves geographic notes, repeats buttons, and releases A for one frame when rearming after landing.
4. Remember the raised-ledge exit, falling-enemy braking, and later pit takeoff.
5. At x1390-1490, wait before the piranha section, then resume. r35 issued exactly 60 game frames of wait in the first win (one simulated second). r36's 90-frame target produced 92 frames in its first win because decisions use four-frame intervals.

The last lesson is especially consequential: removing only it produced 0/10 passes under the final controller. Failure traces reached the plant while it was higher; winning traces encountered it lower in its cycle. Waiting also changes goomba timing, so this comparison does not isolate the plant cycle alone. These are deliberately stage-specific, hand-authored System2 lessons; the model weights are unchanged.

## Evidence and replay

The first win was attempt 47/r35 (`flag_get=true`, terminated at x3161), followed by 48/r36. Attempts55/56 repeated the wins. Every trial starts fresh. `results.json` contains per-run hashes, outcome, frame counts, and policy latency. `round-00.md` through `round-05.md` preserve reflection rationale. `offline-probes.json` contains 40 additional recorded-state inference probes; those did not advance an emulator and are separate from the 100 gameplay attempts.

All 100 raw JSONL trajectories, exact profiles, source snapshots, stdout, a portable manifest, and six representative videos are downloaded under `deliverables/djev-reflection-100/`. Its `verification.json` records exact local replay checks. MP4s play at 60 emulator frames per second; that is not the measured wall-clock inference speed.

Watch attempt 47 for the first success,81 for the no-wait failure,82 for the no-memory stall,22 for the falling-enemy failure, and1 for the early baseline. The package index links every trace and representative video.

## Run the winning setup

```sh
ssh amd 'cd /home/juc049/projects/mario-amd/harness && scripts/run_amd_djev.sh'
```

The wrapper now defaults to `prompts/reflection/r35.json`; new manual runs go to `runs/djev-reflection-play` and do not alter the closed 100-attempt experiment. Simulator CPU and model GPU communicate through `http://127.0.0.1:18515/v1/systemone`. The model returns `dgemma`; config identifies `DiffusionGemmaForBlockDiffusion`, BF16. Physical GPU7 maps to HIP ordinal4. No model/GPU restart or hosted API key transfer was required.

Frozen validation median per-decision latency was approximately 109-111ms under concurrent load. Each reflection decision makes one structured request; this includes model/service contention. The model server itself and its serving configuration were not changed. 55 tests pass on both Mac and AMD; Ruff and whitespace checks pass locally.

The batch runner hard-caps reservations at 100. This experiment is closed; all jobs finished. To inspect a downloaded JSONL without model calls:

```sh
.venv/bin/mario-jev --replay /absolute/path/to/trajectory.jsonl
```

## Final audit

All 100 traces replayed exactly on the Mac, including 24 completions. All six selected videos exported successfully. Validation and ablations used the identical source snapshot `97bdd4572934c91d01b96f14a392fa4f8c90b360fd461ef385877932a036c021`; only the designated profile memory changed. The runner reserved exactly 100 attempts and reported no process errors.
