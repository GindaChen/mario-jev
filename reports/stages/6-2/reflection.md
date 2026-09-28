# World 6-2

## Verified result

Profile r27 cleared fresh attempt 043 in 518 decisions, reaching x=3449. Exact replay and video export passed. Winner and runtime metadata were uploaded to AMD. Remaining exploratory trials were stopped after verification; their partial traces and cancelled/error statuses remain in the ledger.

Trace: `runs/stages/6-2/batches/043-stage-6-2-r27/20260928T060528104847Z.jsonl`.

## Reflection history

The initial infrastructure error occurred before gameplay and remains in the ledger. All counted gameplay attempts started fresh. Early pipe waits and short hops handled the first plants. r13 reached x=1348 twice after braking and waiting on the pipe near x=730. A phase wait before x=1160 moved the next plant cycle; r16 reached x=1408.

r17 uses a short four-frame jump from the pipe near x=1280. This lands earlier on the next pipe, so Mario launches before reaching the taller plant. Progress increased to x=2178. A direct motion classifier over x=2080..2240 makes Mario jump promptly from each pipe and advanced to x=2451.

Delaying the next takeoff until after x=2357 cleared that plant and reached x=2685. The nearest reported threat there is a high plant, while the actual collision was a goomba below it. Eight-frame short hops from x=2600..2735 pass the goomba while remaining below the plant, reaching x=2862.

Walking farther across the last pipe failed at x=2784 because its plant was still exposed. The successful r27 instead asks a direct binary question about whether `note_elapsed_frames.last-pipe-phase` is below 60 while x=2740..2775. Waiting beside the pipe changes the plant phase. Once the timer expires, the model jumps, clears the remaining pipe cluster, and finishes the stage.

## Limits and evidence

This is an independently initialized stage clear with a stage-specific reflected prompt. It is not evidence of a continuous full-game run. The winning trace retains every DJev request and response, the immutable prompt snapshot, and the source snapshot. The existing grounded A-release mechanic was unchanged. No ROM/RAM edits, saved-prefix continuation, or diagnostic scripted actions were used in the counted clear.

## Final attempt ledger

See [attempt-ledger.md](attempt-ledger.md) for every reserved trial, including infrastructure failures and cancelled partial candidates.
