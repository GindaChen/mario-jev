# World 5-3

## Verified result

Profile r16 cleared fresh attempts 021 and 023. The first winner, attempt 021, completed in 285 decisions at x=2425. Exact replay and video export passed; winner and runtime metadata were frozen and uploaded by the parent.

Trace: `runs/stages/5-3/batches/021-stage-5-3-r16/20260928T055152747963Z.jsonl`.

## Revision chronology

- r01: generic running jumps overshot the first low treetop and failed at x=434. The first reserved attempt had separately failed before gameplay because the new inference server was not ready.
- r02: transferring the 1-3 controller failed against an early bullet at x=183.
- r03: the regional short-hop question conflicted with the global falling question; Mario ran while grounded near x=248.
- r04: explicitly replaced the global question and added verified treetop support tiles 22/23/24.
- r05: shortened the first-hop region to x=235..280 and reached x=761.
- r06: imported the later 1-3 lessons, but failed against a goomba near x=738.
- r07: a jump on the upper platform at x=700..770 reached x=880.
- r08: a short upper-platform hop reached x=937 but missed the moving platform.
- r09: 16 frames of braking in x=790..845 landed before the platform edge and advanced to x=1563.
- r10: a full jump in x=1365..1530 reached x=1611. Some repeats failed earlier at x=882, before the changed region; those failures cannot diagnose the new note.
- r11/r12: delaying the launch by continuing to run caused Mario to walk off the moving platform and fail at x=1486.
- r13/r14: introduced braking and a wait on the platform. Raw decisions showed incorrect timer-interval choices; the model coasted off rather than executing the intended ride. These runs do not establish whether the proposed waiting durations were sufficient.
- r15/r16: replaced the prose sequence with an explicit classification of `note_elapsed_frames.ride-platform` into three numeric intervals. r15's shorter wait still failed. r16 brakes left for 24 frames beginning near x=1330, waits through frame 139, then jumps right. Attempts 021 and 023 completed.

The successful lesson lets the moving platform carry Mario toward the next landing. It is a stage-specific timed instruction, not evidence of general moving-platform reasoning. All counted clears were fresh model-controlled games; immutable prompts and raw request/response traces are retained.

## Final attempt ledger

See [attempt-ledger.md](attempt-ledger.md) for all 23 reserved trials, including the initial infrastructure error and both clears.
