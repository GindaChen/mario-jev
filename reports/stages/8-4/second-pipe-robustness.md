# Elevated second pipe: two-prefix diagnostic verification

Replay-only diagnostics from r65 before decision521 (hidden-block landing2395) and r59 before decision519 (landing2401). Both releaseA/runright4frames before jumping. No live model calls, emulator patches or fresh-clear claims.

Constant air braking beginning2408 or2418 fixes r65's excessive forward speed, but fails r59: a collision at2418 removes forward velocity, and continued left input sends Mario away from the pipe. Therefore braking needs to react to observed speed.

Validated simple air rule:

- `left_jump` if `x >= 2438 OR (x >= 2408 AND horizontal_speed >= 1.0)`.
- Otherwise `right_run_jump`.
- Only after actual grounded feet96: left if x>2440; right if x<2432; otherwise down.

The ground rule must override the air rule to avoid grounded A rearm causing another jump. Down need not be offered before the actual pipe-ground note activates.

Both threshold1.0 and1.25 passed on both source prefixes (4/4) when horizontal_speed was computed from the previous executed action's observed displacement, matching the prompt's measurement. All reached the correct next section at3127/3128. Earlier raw-RAM-speed tests also passed, but the observed-speed checks are the transferable evidence. This is bounded diagnostic robustness across two known starting states, not a measured fresh model success rate.

Evidence: second-pipe-r65-diagnostic.json (8 initial branches); second-pipe-simple-verification.json (4 branches showing the collision regression); second-pipe-speed-verification.json (4 raw-speed branches); second-pipe-observed-speed-verification.json (4 prompt-visible-speed branches), each with its source script.
