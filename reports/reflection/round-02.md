# Reflection after trials5-20

Trial16/r12 reached1650, surpassing prior DJev1331, but its repeat20 died1031. Only a candidate improvement, not reliable. The firstpit remembered takeoff was traversed in16. Final trace290-297: Mario jumps from x1634 at nearzero horizontal speed, peaks with feet144, hits exposed plant at1650. Need running takeoff or stronger stomp rebound before the pipe.

Next compare facts-based compact observations (r13-r16) against four plant lessons attached to the best r12 (r21-r24), two repeats each. 40 separate offline probes (no emulator progression) showed facts prompts follow distance flags and ledge instructions; they also exposed ignored falling-enemy flags. All offline calls and evidence are saved separately. More reflections remain necessary.

Code fix: once the reflection controller activates, keep it active after retreating across its activation coordinate. Earlier hybrids accidentally switched back to the old controller during retreat. Keep retrieval memory attached to left maneuvers. Explicitly preserve this source change in perattempt source snapshots.
