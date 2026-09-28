# Reflection after trials1-4

All four failed. Unified-only r01 stalled at852; remembered r02 reached1138 but retreated and died1090; four-step r03 died852; thinking128 r04 died877. More inference compute did not fix the controller on these single runs.

r02 late trace: jumps under low ceiling while moving left; when landing near a goomba, four-frame mechanical A rearm delay advances into collision. Try one-frame rearm separately. Avoid rewriting stable early behavior: r05-r08 use the prior DJev d1 controller until a specified x, then the unified memory controller. Geographic pit notes specify run until1260, then launch; this is deliberate stage-specific System2 guidance, not a blind test or replay script. Repeat each variant twice (trials5-12).
