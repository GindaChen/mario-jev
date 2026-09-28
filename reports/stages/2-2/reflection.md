# World2-2

Underwater baseline r01 uses alternating A press/release strokes when feet_y>80, otherwise swims right without ascending. Same AMD-local DJev, fresh starts, explicit stage-end success criterion. Unlike ground jumping, underwater strokes need repeated A presses even while airborne; the prompt uses the observed jump_held flag.

r01 reaches1234, gets stuck above a middle opening, and is caught by a Blooper. Raw tiles at1248-1280 show ceiling through y80 and floor beginning160. r02 changes the swimming target to feet140 over1100-1400 so Mario descends into the opening before arrival.

r02 clears the opening but is caught by a Blooper while ascending back to the upper route at1456. r03 keeps the middle-depth target through1700 instead of returning upward at1400.

r03 gets past the Blooper but stalls1618 at a coral column spanning y80-144. r04 dives below it (feet target196 after1500); r05 returns to the upper route at1520, after the earlier Blooper encounter but before the coral.

r04 bottom route stalls1906 against rising terrain. r05 upper route gets farther, then stalls2082 under another ceiling lip (tiles2096-2208 at y64). r06 descends to the middle target over2070-2400, after the preceding floor rise.

r06 descends too late, pauses at the ceiling lip, and is hit at2095. r07 begins the second descent at1980, targeting passage clearance before arriving at the lip.

r07 arrives at the opening without the earlier long stall but collides at2088. r08/r09 vary only the second passage target depth (120/160 instead of140), testing a route above/below the crossing enemy while preserving prior lessons.

r08 target120 clears the second opening and reaches2668; r09 target160 gets trapped by the preceding raised floor and dies2077. r08 then walks off a tall underwater column at feet80 into a fish. r10 targets feet48 from2520 to2900 to stroke upward before leaving the column and pass above the fish.

r10 clears the fish/coral route and reaches2994 at the exit wall. The horizontal exit pipe is at y112-144; r11 descends to the feet140 target after2900 to enter the pipe from the side. Completion is still required after the exit transition.

r11 stalls3010: it strokes upward again at feet142 and never settles at the exit-floor height144. r12 raises the stroke threshold to208 in the exit region so Mario can sink to the pipe entrance while continuing right.

r12 enters the exit pipe successfully at decision437. The overworld exit reuses x2872+, so the swimming/exit notes also apply to the final staircase and stall2914. r13 uses the recognized wall fact to jump grounded stair approaches and sustains rising jumps in the exit region; underwater coral/pipe tiles do not set this wall fact.

r13 changes underwater ascent timing and stalls2994 before the pipe. r14 restores r12 swimming behavior for the first100frames of the exit-depth note, then uses grounded/rising jumps for the overworld stairs. This is an explicit timed stage lesson derived from r12 transition at about84frames, not a general area detector.

r14 COMPLETED the stage at x3161 in478decisions. Fresh start, DJev chose every action, exact replay verified, winning trace/profile/video saved. First verified clear accepted; advancing to2-3.
