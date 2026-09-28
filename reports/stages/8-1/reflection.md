# World 8-1

Parallel campaign, AMD-local DJev on18515. Fresh-start baseline transfers 2-1/r01.json. Only actual stage-end completion followed by exact replay is a pass. Internal pipes are part of normal stage traversal; world-skipping warp optimization is deferred.

r01 fails at x=561. r02 tests the simpler sustained-running-jump motion classifier as an alternative baseline before adding local lessons.

r02 fails at the pipe plant. r03 pauses near the pipe for90frames, then attempts the crossing.

r03 inspected: next variants adjust the next failing maneuver (8-1 short hop after high pipe;8-3 delay jump until past overhead bricks;8-4 initial running buildup with2frame decisions). Prior failures and all parameters retained.

Next local adjustment:8-1 delay takeoff before3536-3632gap;8-2 delay hop across alternating single-tile gaps;8-3 wait before second plant;8-4 back up first to build running speed on the top initial ledge. New notes explicitly replace the global question to avoid conflicting instructions. Root added tested opt-in replace_instructions; defaults unchanged.

Next reflection:8-1 delay takeoff before3792gap/plantpipes;8-2 short jump after high pipe to avoid landing on flying Koopa1440;8-4 walking descent to lowest initial step before launching, since earlier top-step jumps hit the ceiling.

r06 still selects jumps against the action prose; r07 uses an explicit x-comparison question for the approach.

r07 correctly delays jumping but collides with a goomba3693. r08 replaces that delay with a short hop over the enemy cluster, aiming to land before3792gap.

r08 short hop lands on the third goomba3735. r09 holds A for8frames instead of4, aiming to clear the full cluster but still land before the gap.

r09 clears the first enemies but gets a low stomp rebound and lands at the gap edge3786. r10 holds A through the stomp region to produce a higher rebound over the pipes.

r10 did not increase stomp bounce height; it still lands at3786 and falls into3792gap. r11 returns to r09 and brakes LEFT while falling in3711..3780, aiming to land earlier before the gap. Grounded/rising remains model-selected right+jump.

r11 now reaches4677 but overshoots the last safe floor, falling into4640..4688gap. r12 shortens the jump off4480stair to land before the gap.

r12 clears the later gap but lands on pipe plant5688 after a full jump off5531pipe. r13/r14 shorten this hop (grounded only vs8frames), aiming to land before the next pipe and jump again.

r13 reaches5847, hitting the tall5856stair wall (top80) while feet90 at apex, then falling into5840gap. r15/r16 brake and release jump at5800/5810 to land on intermediate5824stair(top112), then launch again. r14 medium hop failed earlier at5784.

r15 PASSED:655 fresh decisions,x6009,actual flag. Earlier brake5800 succeeds landing on intermediate stair; later5810 r16 fails5843, demonstrating timing sensitivity. First winner replay/export in progress; no new live validation launched.

Exact replay verified and video exported. Frozen winner/runtime and deliverables copied toAMD.
