# World 1-3 reflection experiment

Scope: AMD-local DJev, fresh independent stage starts, original paused-during-inference simulator. This is not the asynchronous-control experiment. World 1-2's closed 100-attempt dataset is preserved.

Initial baseline r01 inherits r35 mechanics but removes all 1-2 memory. Failed at x423 by overshooting the first platform. r02 moves pit takeoff threshold from24 to64 pixels: reaches x701 but retreats at a ledge due to an overhead enemy. r03 prioritizes gap jumps over overhead-enemy retreat: x774, but jumps into the underside of the next raised platform. r04 attempts earlier repeated jumps through x430-640: x783, same underside failure. r05 brakes the earlier platform landing: x773, does not resolve the next raised platform.

r06/r07 add a compound conditional ascent brake; both reach x774. Trace inspection shows the intended braking action was not selected, so these are unsuccessful prompt-compliance attempts, not evidence that braking cannot work. r08/r09 simplify the note to a two-choice rising-versus-other rule over a narrow coordinate interval.

All profile JSONs are retained under prompts/stages/1-3. Initial r01/r02 traces are under runs/stages/1-3/r01 and r02; subsequent runs have immutable profile and source snapshots in runs/stages/1-3/batches. The batch runner now accepts --world/--stage and refuses mixing stages in an existing manifest. No model weights or serving settings changed.

Further inspection: platform metatiles 0x16-0x18 are not in the existing solid-surface classifier, so generic gap facts are unreliable here. r08 simplified ascent braking reaches x898; r09 reaches x648. r10/r11 change later gap thresholds but reproduce r08 because the computed gap distance is already zero. Raw terrain shows the high platform ends at752 and a lower platform spans800-864 at feet208. r12 therefore teaches walking off the high platform instead of jumping and overshooting the low landing. This keeps the controller unchanged and records the observation limitation explicitly.

r12 lands at x849/feet208 but its no-jump interval lasts through x860, walking off again. r13 ends that interval at835 so grounded re-launch is available.

r13 reaches966 but launch from849 is too late for the next moving platform: ascent reverses near885 before maximum jump height. r14/r15 test12/16-frame braking during the preceding drop, aiming to land earlier on the low platform and start the next ascent earlier.

r14 reaches959; r15 with16-frame drop braking clears the moving-platform section and reaches1178. Death is collision with vertically moving object_0f at x1184 during a jump launched from1157. r16 launches earlier from the preceding low platform; r17 additionally brakes its ascent to land farther left before the koopa.

r16 clears the flying koopa and reaches1520; r17 reaches1244. r16 jumps off the high platform at1286 and overshoots the moving platform. r18 adds a controlled drop over1270-1375. Traces also expose screen-top y wrap in the existing motion estimate; this is retained as an observation limitation, not silently fixed during prompt search.

r18 walking off misses the moving platform side at x1345 and dies at1372. r19/r20 test a short hop with A released immediately after takeoff; r20 also brakes while rising.

r19 short hop lands on first moving platform at1372/feet128 but repeats a short hop and misses the next platform. r20 brakes too much and reaches1444. r21 ends the short-hop note at1360, retaining the first landing and allowing a full jump from1372 to the next moving platform.

r21 full second jump overshoots the second moving platform, reaching1574. r22/r23 test12/20-frame held-jump cutoffs for a medium second hop.

r22 lands on the second moving platform at1485 and the following static platform at1607, then collides with a koopa after landing at1718. r23 overshoots the static platform and reaches1746 only while falling (not better survivable progress). r24/r25 test ascent braking to land farther left before the koopa.

## First wins

r24 and r25 BOTH completed normal World1-3 at x2425 in252 and249 decisions. These are overall discovery attempts24 and25 (batch IDs22/23, plus the two initial baselines). No replay prefix or state edits were used. Freeze these profiles and run three fresh repetitions each before declaring repeatable success.

## Reproduce

AMD command: `cd /home/juc049/projects/mario-amd/harness && scripts/run_amd_stage.sh 1 3`. The stage wrapper uses r24 copied byte-for-byte as prompts/stages/1-3/winner.json, frames4, fresh start, 2000-decision cap, and a separate stage-play log directory. This remains stage-specific reflection with unchanged weights; it is not generalization or realtime control.

## Frozen validation

All6 fresh validation runs passed: r24 3/3, r25 3/3. Each profile therefore has4/4 observed wins including discovery. Total31 fresh runs:25 discovery (2 passes),6 validation (6 passes),8 passes overall. These use the same reset seed and stage-specific coaching, not held-out robustness.55 existing tests pass.
