# Exact-arrival-phase water diagnosis: r52

This is a bounded replay-only experiment:20 branches, no fresh DJev calls, no ROM/RAM changes. Every branch resets normally and replays r52 through decision775 (result x346; decision775 began x343), preserving the actual live water-entry phase. Diagnostic source and every branch history are in `water-r52-diagnostic-source.py` and `water-r52-diagnostic.json`.

## Measurable middle-passage maneuver

1. Use ordinary repeated-stroke targetfeet128 until x>=540.
2. Hold left16frames with A released, then release all buttons for20frames.
3. Resume rightward strokes with targetfeet176: release A if held; otherwise stroke only if feet>176.

This crosses the previously blocking firebar near644 and reachesx887 before a later firebar. All18 combinations of trigger540/560/580, pause20/40/60, target176/192 crossed the644 hazard; best reached894. Two unmodified target112/128 baselines both died630. These are diagnostic successes at the middle obstacle, not successful stage runs or an estimated model-policy success rate.

Rendered frames at480/540/600/630 show the geometry: the640 firebar hangs from an upper pillar, with a lower pillar below leaving a narrow opening. Continuing at the baseline height intersects the rotating flame near the pillar. The brake/release interval changes both vertical position and flame phase, so the results do not isolate which factor contributes most.

The next observed diagnostic bottleneck is the firebar whose runtime origin is900: the chosen branch diesx887, feet160; a squid is also nearby. No branch reached the normal exit. A fresh model-controlled trial must independently reproduce this maneuver.

## Bounded continuation reaches the normal exit (diagnostic only)

Ten additional branches varied late target80/96/112/128/208 beginningx760or800. The eight upper-target branches diedx799/820. Both target208 branches passed the later firebar and exited through the normal water pipe when target switched to144 atx990. Two explicit replay verifications confirmed destinationroom41980, spawn4152, no death. This matches the statically decoded castlepage16 destination.

Complete candidate for a fresh model-controlled test: target128 to540; brakeleft16 and wait20; target176 until760 (800also passed); target208 until990; target144 through horizontal exit. Maintain the repeated-stroke rule: releaseA if alreadyheld, otherwise stroke only if feet exceeds target. Live model reproduction remains required. Files: water-r52-late-diagnostic.json (10branches), water-r52-exit-verification.json (2destination checks), with source scripts beside them.
