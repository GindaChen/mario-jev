# World 6-4

## Verified result

Profile r33 cleared fresh attempt 040 in 243 decisions, reaching x=2259. Exact replay and video export passed. Winner, runtime metadata, and complete deliverables were uploaded to AMD.

Trace: `runs/stages/6-4/batches/040-stage-6-4-r33/20260928T060404698863Z.jsonl`.

## Opening revisions: r01–r16

The first reserved attempt failed before gameplay because the inference server was not ready. The transferred castle controller then needed stage-specific jump timing.

r02's launch near x=310 hit a firebar at x=341. r03 delayed the launch to x=380 and cleared the first gap but fell at x=556. r04 added verified castle tile 98 to terrain facts. Waiting near the gap in r05 let inertia carry Mario off the edge, failing at x=422.

r06 used a 12-frame first hop and reached x=580. A four-frame second hop in r07 failed at x=518. Initial waits of 60/120 frames in r08/r09 did not clear the section. Development-only replay branches swept jump durations and found several combinations that reached x=662 alive; these scripted branches are excluded from attempt and clear counts. r10/r11 encoded 12/8-frame second-hop hypotheses as prompts for fresh model-controlled games. One- and two-frame action-interval trials of r11 also failed. r12 transferred the 3-4 opening lesson and failed earlier at x=327. r13/r14 tried longer first-hop holds without clearing the section.

The x=580 collision was ultimately identified as the third jump into the rotating firebar centered near x=596. r15/r16 sustain an existing rise but run when grounded or falling in x=550..620/660. Both consistently reached x=1178. The parent took ownership after attempt 023 and used endpoint 18515 for later revisions.

## Firebar corridor: r17–r30

r17 stayed low in x=1140..1260 but still died at x=1190 during the firebar sweep. The floor rises at x=1216, so permanent running was insufficient.

r18–r20 returned to r15 and proposed waits of 24/48/72 frames near x=1100. Their realized actions were identical: inertia carried Mario out of the note region after 16 frames, before any threshold. This was one effective slowing maneuver, not a comparison of three executed wait durations. All reached x=1382, where the next full jump entered the overhead firebar.

r21/r22 shortened that jump to 8/12 frames but still collided near x=1364..1385. r23–r25 replaced the accidental coast with an explicit 16-frame brake and total phase timers of 40/72/104 frames in a wider region. The distinct waits were actually executed, but all failed near x=1363; this does not establish phase causality because later hazards may only spawn as the camera advances.

r26/r27 tried a four-frame hop; r26 also ran low in x=1350..1450. Both failed near x=1370. r28–r30 instead paused after the relevant hazards had spawned: brake in x=1250..1320, then depart at local frame 24/48/72. The shorter timings failed at x=1367/1350. r30 crossed the corridor and reached x=1992, where an incoming Bowser fireball hit Mario while climbing from the lower pocket to the ledge.

## Final approach: r31–r34

r31/r32 waited 40/60 frames in the low pocket before jumping onto the ledge. r31 passed the incoming fireball, crossed the bridge, and ran under airborne Bowser. It then jumped too early near x=2208 and collided with his rear body, ending at x=2214. The longer r32 wait failed at x=1955.

r33/r34 extended the low running section through x=2235/2245 before the axe step at x=2256, transferring the successful 7-4 lesson. r33 completed. r34 waited too long to jump, stalled against the wall near x=2242, and died at x=2243. The first r33 clear was frozen and replay-verified; no additional validation trials were launched.

All counted clears started fresh and used DJev-selected actions with the existing grounded A-release mechanic. No ROM/RAM changes or scripted diagnostic continuations count as clears.

## Final attempt ledger

See [attempt-ledger.md](attempt-ledger.md) for all 41 reserved attempts: one initial infrastructure error, 39 gameplay failures, and one clear. Diagnostic replay branches are listed separately in this report and excluded from those counts.
