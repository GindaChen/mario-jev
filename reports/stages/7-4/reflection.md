# World7-4 reflection

Transferred castle profile loops: x wraps by1024 after wrong maze branch. Found unrecognized castle tile98; opt-in tile fix reveals upper96/middle160/bottom208 platforms. Geometry-only route climbs first upper platform then falls through gap around800, takes bottom route and loops. Testing sustained/short jumps from750/780 and another upper jump near1040. Looping attempts remain failures regardless of max_x.

All trials start fresh on AMD-local DJev port18518. DJev selects every live action; geographic memories and scalar thresholds are offline GPT coaching. Passing requires explicit stage completion followed by exact action replay.

External route semantics verified from primary disassembly: https://gist.github.com/WillSams/678a2d8a49d3f01e1d6e0362f83d1fbc (saved ../reference/SMBDIS.ASM). Maze checks require grounded exact heights: first bottom208/middle160/top96 feet, second top96/middle160/top96. Current map geometry determines local takeoff lessons; no maze flags or ROM values are modified. r08 clears first maze; r11 jumps from raised platform near1515 to pass firebar. r17/r18 enter second middle route via a short jump near1820 and rise to upper route near2070; they pass both mazes, reach2836, then hit a fireball. Testing earlier fireball thresholds80/112.

r19/r20 increase fireball reaction distance to80/112 after2500 and reach3245/3249. Bowser is airborne above Mario, so generic enemy filter ignores him; then a step-triggered jump collides as Bowser descends. r21–r23 add local full-speed Bowser leaps starting3130/3150/3170.

Early Bowser leap trials r21–r23 collide with airborne Bowser. r24–r26 instead preserve the safe underpass, delaying the axe-step jump until after3245/3255/3265. All three fresh trials completed x3286. First winner r24 replay verified and exported;26 attempts total. This completes all four World7 stages independently.
