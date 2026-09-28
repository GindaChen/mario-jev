# World 8-2

Parallel campaign, AMD-local DJev on18515. Fresh-start baseline transfers 2-1/r01.json. Only actual stage-end completion followed by exact replay is a pass. Internal pipes are part of normal stage traversal; world-skipping warp optimization is deferred.

r01 fails at x=333. r02 tests the simpler sustained-running-jump motion classifier as an alternative baseline before adding local lessons.

r02 fails during the opening stepped terrain. r03 keeps the motion policy but reduces action duration from4frames to1frame so it can respond to brief landing opportunities. Frame granularity is recorded in config and manifest.

r03 one-frame timing changes the opening and dies213. r04/r05 return to4frames and pause24/48frames near255 before jumping up the stairs, to alter overlap with the falling Spiny at335.

Next local adjustment:8-1 delay takeoff before3536-3632gap;8-2 delay hop across alternating single-tile gaps;8-3 wait before second plant;8-4 back up first to build running speed on the top initial ledge. New notes explicitly replace the global question to avoid conflicting instructions. Root added tested opt-in replace_instructions; defaults unchanged.

Next reflection:8-1 delay takeoff before3792gap/plantpipes;8-2 short jump after high pipe to avoid landing on flying Koopa1440;8-4 walking descent to lowest initial step before launching, since earlier top-step jumps hit the ceiling.

r07 short hop still meets the Koopa. r08 brakes while descending to land farther before it, then launches the next jump.

r08 braking clears the Koopas and reaches2477, falling into the long gap after takeoff2261. r09 delays takeoff until2331; geometry shows far ground2464.

r09 runs into a plant2273 when it suppresses the pipe jump. r10 retains a short hop over the pipe, aiming to land on the small2352platform before the long gap.

r10 clears the long gap, then lands off the2616pipe and jumps into a flying Koopa2666. r11 brakes on descent to land on the pipe and launch the next jump from its higher surface.

r11 clears the pipe Koopas and reaches2910, but launches at2886 too late to clear goombas on the final stairs. r12 brakes on descent only in2850..2890, after the2848gap, aiming to land earlier on2864floor and regain jumping clearance.

r12 now reaches3210 but hits flying Koopa while slowly climbing stairs after landing against their wall. r13 brakes on descent3090..3175 to land earlier and launch with more clearance.

r13 lands earlier at3141, but still meets the flying Koopa at3202. r14-r16 retain that earlier landing and test total local timers40/64/88 before leaving the ground. This shifts enemy phase without changing earlier route.

r14 PASSED:420 fresh decisions, x3449, flag reached. r15/r16 longer waits failed3178/3168, so a longer wait is not uniformly safer. Exact replay verified; winner, runtime and first-win.mp4 frozen. No additional validation trials launched.
