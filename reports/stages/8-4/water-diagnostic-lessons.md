# Bounded underwater replay diagnostics

These40 branches are replay-only diagnostics, not fresh model attempts or clears. All replay r44 before decision637, execute the previously tested normal third-pipe maneuver, and begin swimming after left_jump28/down24/left18/down120. That extra final down duration can change water-enemy phase relative to a fresh controller that reacts immediately when room44738 appears.

All swim decisions hold2 emulator frames. A stroke is right_run_jump only when A was released and feet exceeds target; otherwise right_run. This matches a promptable threshold controller and continuously releases/represses A.

-12 baseline branches: targetfeet80/96 stalls atx162 because of entrance geometry;160 also stalls there.144 dies nearfirstfirebarx302.112/128 passes the opening and first bars, reaching622/630 before colliding near the ceiling firebar whose runtime origin is644.
-14 middle branches: firsttarget112, then target64/80/96/128/144/160/176 after440or520. None passes middlebar; best reaches639. Higher routes die earlier around610; lower routes reach632–639 but still intersect a rotating segment.
-8 phase branches: firsttarget112, at520or550 brake left16 while swimming, hover for total24/40/56/72frames, then resume. None passes middlebar; these limited delays are not proof that waiting cannot work.
-6 earlier-descents: target112 then176/192/208 after340or400. Target176 reaches630;192/208 hits the earlier floorbar at471.

Useful prompt lesson: target112–128 through the opening; do not simply swim at top or bottom. A successful middle passage needs a different phase/timed movement or more precise positioning. No branch reached the exit, so the normal exit-depth144 remains a static-geometry inference, not an empirically verified underwater traversal.

Source scripts and complete histories are preserved beside each JSON report: water-diagnostic, water-middle-diagnostic, water-phase-diagnostic, water-low-diagnostic. The live owner has independently reached water with r52; its exact arrival phase should take precedence over these older-prefix branches.
