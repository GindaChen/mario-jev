# World 5-4

## Verified result

Profile r21 cleared fresh attempt 027 in 242 decisions, reaching x=2259. Exact replay and video export passed; winner and runtime metadata were uploaded to AMD. All four fresh trials of r21/r22 completed.

Trace: `runs/stages/5-4/batches/027-stage-5-4-r21/20260928T055351038163Z.jsonl`.

## Reflection history

The transferred 2-4 castle policy needed stage-specific timing. A wait near x=990 moved the firebar phase and advanced beyond x=1700. Delaying the launch until x=1571 allowed Mario to land on the narrow ledge at x=1721, but jumping immediately met the lava bubble at x=1744.

Three-action brake/wait/jump prose was unreliable: the model sometimes selected the wrong timer interval and coasted off the ledge. The winning r20 ancestor asks a direct binary question about whether `note_elapsed_frames.ledge-brake` is below 36, beginning at x=1688. This brakes before landing, then launches after the bubble moves.

The final failure was a jump into the lava bubble at x=2096. r21 sustains an existing rise but does not start a new jump from x=2050 through 2120, passing beneath the airborne bubble. The rest of the transferred castle policy clears Bowser and the axe.

All counted clears started fresh and used DJev-selected actions with the existing grounded A-release mechanic. Raw failed runs, immutable prompt snapshots, and request/response logs remain in the batch directory.

## Final attempt ledger

See [attempt-ledger.md](attempt-ledger.md) for every reserved trial, including infrastructure failures and cancelled partial candidates.
