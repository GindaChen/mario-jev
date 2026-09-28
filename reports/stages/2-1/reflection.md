# World2-1

r01 baseline reaches735, landing on a piranha at pipe736 after jumping over approaching goombas at621. r02/r03 test30/60-frame start waits to change hazard timing without changing mechanics. Fresh attempts only; explicit completion required.

r02/r03 reproduce exactly the same spatial failure at735; start waits do not change this encounter. r04/r05 instead use a short, early goomba hop over570-660, with enemy thresholds64/80, aiming to land before the pipe and launch a second jump.

r04/r05 both reach751: the short hop bounces on a goomba, causing a late pipe launch711 and insufficient horizontal speed after hitting its side. r06/r07 instead brake the preceding block jump, targeting a higher/earlier landing before the enemy-and-pipe sequence.

r06-r09 retain the same pipe collision (734-739). r10 later enemy threshold24 reaches741; r11 threshold16 is too late and dies645. r12 separately tests holding A through descent (separate sustain-probe manifest). r13/r14 build on r04's short hop, then wait60/90 frames beside the tall pipe over700-760 before climbing it. This targets plant phase after enemy activation rather than the ineffective initial wait.

r12 holding jump through descent reproduces735. r13 wait60 clears the first pipe but dies1406. r14 wait90 reaches1610, landing immediately beside a goomba before another tall pipe. r15/r16 add ascent braking from1500/1480 to land earlier with room for the next jump.

r15 reaches1818; r16 earlier braking reaches1969 but clips a piranha after a late climb onto pipe1952. r17/r18 reuse the successful wait-beside-pipe lesson with90/60-frame waits over1920-1980. All earlier lessons stay fixed.

r17/r18 both clear the next pipe and reach2281, but an unnecessary jump at2053 from an elevated brick row carries Mario directly into the next ground pit instead of landing before it. The trigger is a plant far below the current ledge. r19 suppresses that jump; r20 tests a short hop instead.

r19 drops onto a koopa and bounces into the pit (2269). r20 short-hop alternative clears the pit and reaches2680. Flying koopas (object_0e) approach from above, so the baseline enemy dy>=-8 rule triggers too late. r21 starts a jump as soon as grounded over2620-2750.

r21 clears the flying koopas and stalls at3026 against a160px wall. A springboard (object_32, tiles0x67/0x68) sits at3008; Mario has moved just past it. r22 targets the springboard's x band and holds jump vertically until high enough to cross the wall. The note accounts for wrapped y coordinates above the screen; this is explicit stage-specific guidance.

r22 reaches the spring but retreats while it is compressed: the target band ends3010, while Mario lands at3018. It produces only low bounces and stalls. r23 widens the spring band to3000-3024 and explicitly holds A during compression.

r23 stays just past the spring at3022 and only performs normal jumps. r24's non-jumping retreat becomes trapped between the spring and wall. Ten diagnostic branches on AMD replayed r21's prefix and tested five target x positions, with/without one-frame A rearming. No-rearm branches all fail. With rearming, targets3004 and3012 clear the wall past3072. The important correction is to JUMP LEFT back onto the spring, not walk left against its side. r25/r26 turn those findings into DJev stage lessons for full fresh runs; diagnostic branches are not counted as stage clears.

r25/r26 fail to reproduce the successful diagnostic control rule reliably; e.g. r25 chooses vertical jump at3026 where its prompt requests jump-left. r27 splits the x regions into separate retrieved notes, leaving only a height decision to DJev in each region. This is a prompt simplification prompted by exact response inspection, not a new physics hypothesis.

r27 with120-decision stall limit stops during another bounce attempt. The repeat with600-decision stall allowance COMPLETED at3193; the original limit cut off the maneuver too soon. r28 adds an optional measured Boolean `above_maneuver_clearance`, computed only for notes requesting a height threshold (including explicit screen-top wrap handling), and makes each spring choice a true/false decision. It also removes the misleading manual-rearm alternative from the approach note: code already handles A release. This observation-only controller change is covered by a test that verifies the measured fact, note scoping, and preservation of the model-selected action.56 tests pass.

SUCCESS: r27 with600-decision stall allowance is the first completed fresh run (overall attempt28, batch27 plus the separate r12 probe). Its completion was confirmed while r28 was already running; r28 is an additional experiment, not required for this win. Freeze the first r27 success and advance to2-2.

r28 additional height-fact experiment did not improve the springboard result (stalled3027 after1068 decisions). The frozen winner remains r27 under the original observation scheme, with600-decision stall allowance. No claim that the optional height fact caused the win.
