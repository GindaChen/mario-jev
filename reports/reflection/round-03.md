# Reflection after trials21-36

Facts profile r14 (enemy40) reached1197 and1190 in trials22/30; enemy32 died680 and enemy48/56 regressed. The plant variants were not reached; all failed near the earlier ledge, so their plant hypotheses remain untested. Do not select them as proven fixes.

Offline probes predicted r14 would ignore falling enemies. Next batch37-44 adds an explicit priority brake for overhead enemies at48/64/80px, plus a short-hop variant. Planned alternatives r29-r32 brake to zero then wait rather than retreat continuously. This addresses the new failure mode of retreating into enemies behind.

Measured facts are calculated in code (distance and geometry Boolean features), but DJev still selects every live controller action. Stage memories intentionally constrain candidate actions at known bottlenecks; the experiment tests a stage-specific coached controller, not general zero-shot play.
