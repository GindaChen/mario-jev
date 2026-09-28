# World 1-4

Success criterion: explicit game completion from a fresh independent stage start. Save first winning prompt and exact replay, then advance to the next stage. No warp-specific handling in this campaign.

r01 baseline (1-3 generic controller without stage notes, pit24) misses the far bank after first lava jump; max556. The jump starts383, while the floor edge is416. r02 changes pit takeoff distance to0, aiming to launch407 and reach the raised far bank before descending below it.

r02 fails earlier at234: the first short gap needs the original timing. r03 restricts the late-takeoff threshold to x340-420, preserving the first gap behavior.

r03 clears the lava and reaches776, but selects repeated left actions near a firebar pivot. The generic criteria still offered retreat despite forward instructions. r04 removes the unused left choice and keeps the two forward actions.

r04 reaches1592 and collides with approaching object_15 (Bowser fireball): at1568 it is42px ahead, then at1580 only24px ahead, leaving too little clearance time. r05 uses enemy jump threshold64 after1500 to launch on the preceding grounded decision.

r05 survives fireballs but stalls at1842. Raw terrain reveals a raised castle step (tile0x62), missing from the existing generic solid tile set. r06 adds a local jump lesson over1800-1930 rather than altering the observation decoder mid-search.

r06 clears the first step but stalls at1954 against another0x62 step. r07 extends the repeated grounded-jump lesson through the remaining castle section.

r07 reaches2200 but lands beside Bowser (object_2d), whose left edge is only9px away at landing. r08 suppresses new jumps over2030-2100 so the final jump starts closer to Bowser and crosses him at altitude.

SUCCESS: r08 completed at2260 in225 decisions on fresh discovery attempt8. First clear is sufficient under the user's updated criterion. Freeze r08 and advance to2-1.
