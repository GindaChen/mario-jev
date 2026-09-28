# World 6-3

r01 transfers a prior-stage controller as an initial hypothesis. The first reserved run hit an infrastructure error before any decision: the adapter health endpoint was ready before the newly started model server. The error is retained in the attempt ledger and does not count as gameplay evidence. Retry only after a real choice request succeeds.

## Earlier platforms

The early spring-centering attempts failed because horizontal inertia carried Mario beyond the target. r04 added verified treetop tiles 22/23/24 to the terrain facts. r05–r07 still looped or fell. r08 bypasses that spring by delaying the preceding platform launch through x=529, advancing to x=1206. A second delayed launch through x=990 in r10 advanced to x=1953 and exposed the final spring as the next bottleneck.

## Spring timing diagnosis

Replay-only diagnostic branches from r12 show the final spring can be crossed: brake horizontally to touch it near x=1866 with feet_y=178, release A for 2–10 frames, then hold A through compression. These branches reached x=2042; they are not fresh model clears and must not count as successes. Zero delay or delays of 12+ frames failed. Existing one-frame A rearm disrupts spring compression. Source verification shows `one_frame_rearm:false` does not disable rearming; it makes the release last the normal four-frame action interval. This timing aligned with compression in fresh r21, which reached x=2113.

Profiles r16/r17 encountered the API requirement for at least two choices in the brake question; those errors are retained. r18/r19 fixed the choices but placed the spring-launch region too far right. Actual fresh-run contact is x=1863, so r20/r21 lower its entry threshold to 1860. An initial launch was rejected while an earlier batch held the run-root lock; the later successful launch is recorded in the attempt ledger.

## Later platforms

r22/r23 reached x=2521 four times. They preserve jump through wrapped top-of-screen observations (`feet_y >= 240`) in x=1910..2070. Extending that question throughout x=2800 changed earlier platform timing and failed at 2311, so r26/r27 restored the earlier scope and added a second note only after x=2330. That fixed the wrapped observation but the jump from x=2275 still missed the final platform top by roughly 12 pixels vertically. r28/r29 therefore test short hops between the intermediate falling platforms (x=2320, 2384, 2448), rather than trying to skip them in one jump.

## Verified clear: r29

Fresh attempt 042 completed in 270 decisions at x=2665. Exact replay verification and video export passed; winner and runtime metadata uploaded to AMD. The final fix uses eight-frame short hops across the falling-platform chain from x=2270..2460, rather than attempting to skip the intermediate platforms. This combines the spring timing lesson, scoped above-screen jump handling at x=1910..2070, and the earlier platform launch lessons. All live actions came from DJev choices, with the pre-existing grounded A-release mechanic unchanged.

## Final attempt ledger

See [attempt-ledger.md](attempt-ledger.md) for every reserved trial, including infrastructure failures and cancelled partial candidates.
