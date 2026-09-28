# World 8-3

Parallel campaign, AMD-local DJev on18515. Fresh-start baseline transfers 2-1/r01.json. Only actual stage-end completion followed by exact replay is a pass. Internal pipes are part of normal stage traversal; world-skipping warp optimization is deferred.

r01 fails at x=255. r02 tests the simpler sustained-running-jump motion classifier as an alternative baseline before adding local lessons.

r02 fails at the pipe plant. r03 pauses near the pipe for90frames, then attempts the crossing.

r03 inspected: next variants adjust the next failing maneuver (8-1 short hop after high pipe;8-3 delay jump until past overhead bricks;8-4 initial running buildup with2frame decisions). Prior failures and all parameters retained.

Next local adjustment:8-1 delay takeoff before3536-3632gap;8-2 delay hop across alternating single-tile gaps;8-3 wait before second plant;8-4 back up first to build running speed on the top initial ledge. New notes explicitly replace the global question to avoid conflicting instructions. Root added tested opt-in replace_instructions; defaults unchanged.

r05 COMPLETED at3417 in372decisions; exact replay verified, winner/video saved. Five fresh attempts, one clear. Two plant waits and a delayed jump after low bricks were sufficient for this run.
