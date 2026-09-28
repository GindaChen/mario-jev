# World2-3

Fresh AMD-local DJev runs. r01 starts from the generic hazard-triggered two-action ground policy; r02 tests repeated running jumps over the bridges. Both retain one-frame grounded jump rearming. No scripted action override or warm-start prefix.

r01 dies at567 from a flying fish after running along the bridge; r02 reaches1102 but releases A while still rising at961 and falls into the gap. r03 extends the enemy threshold to96. r04 rewrites sustained running jumps as a single explicit falling exception, preserving the same action set.

r03 repeats the original fish collision; the enemy was above the vertical trigger until too late. r04 sustains jumps better but changes earlier timing and collides512. r05/r06 preserve r02 up to920, delay takeoff to985/997, then explicitly hold A across the64px gap starting1024. These are spatially retrieved maneuver lessons.

r05 still jumps too early (model does not consistently follow the delayed approach) and falls1104. r06 clears the first gap, then falls1578 at the next gap starting1536. r07/r08 retain r06 and add a delayed takeoff at1500/1512 after landing near1439.

r07 delays successfully but collides with a fish1495 before takeoff. r08 diverges even before its changed note and dies217; parallel one-step inference is not reliably action-identical for identical earlier observations. r09/r10 move the second-gap takeoff earlier to1470/1482 to clear the fish as well as the gap.

r09/r10 diverge in earlier trajectories and collide near1000 before the second gap. To test whether stronger decoding follows the basic policy more consistently, r11/r12 use the same DJev model with four denoising steps instead of one: repeated jumps vs hazard-triggered jumps. This changes inference compute, not weights or model/provider.

r11/r12 four-step decoding does not resolve the behavior (deaths806/567). r13/r14 instead phrase the two-action choice as a direct classification of the observed motion field, avoiding motor-planning prose and unrelated conditions. One-step inference restored.

r13/r14 correctly sustain jumps and produce the same path, but land on a flying fish at512. This provides a cleaner baseline for timing reflection. r15/r16 delay the jump normally starting356 until396/432, shifting the landing beyond the collision point.

r15 clears the fish and first bridge gap, then jumps too early at1154 and falls into the1280-1344 gap. r16 falls at the first gap1082. r17/r18 retain r15 and delay the next takeoff to1231/1251.

r17/r18 clear the1280 gap and fall at the1536 gap (max1580/1578). r19/r20 retain r17 and delay the next jump until1481/1501.

r19 clears the third gap and reaches2536, then falls into the gap2496-2544 after jumping too early2360. r20 collides1657. r21/r22 retain r19 and delay the late bridge jump to2441/2461.

r21 COMPLETED at3593 in320decisions. Exact replay verified, winner and video saved. r22 (already in the same discovery batch) falls2920. Total22fresh runs,1clear; no extra validation games launched after first clear. Advancing2-4.
