# Final Bowser maneuver: diagnostic success, not a fresh model clear

The saved screenshot `bowser-failure.png` shows Mario intersecting Bowser's thrown hammer stream while Bowser is below/right. The late-body collision and early jumping failures require different timing; constant low running reached4789 but did not complete.

Eight bounded phase-wait variants from the exact fresh r59 prefix were tested. One combination reached the axe and actual episode completion: brake16, wait80, jump after4670. It was repeated independently and its complete recorded controller sequence passed exact position replay. These are offline diagnostic continuations, not fresh DJev trials or additional stage clears.

Source prefix: `runs/stages/8-4/batches/059-r59/20260928T063310872716Z.jsonl`, all recorded decisions before1093. No RAM/ROM patches or save-state injections. First pipe hop holdsA12frames; run until grounded beyond4288; second hammer-brother hop holdsA8frames; then normal2-frame bunny policy with one-frame grounded A rearm and landing interruption. Low-run region starts4590, preventing the jump otherwise taken at4615.

## Verified phase landmarks

At the first grounded state x>=4610, Mario is exactly x4615, feet160. Relative executed frames:

| Interval | Action | Observed effect |
|---|---|---|
|0–16|left|Brake from4615; drift ends around4641.|
|16–96|wait|Remain safely grounded; settle at4639.|
|96–122|right_run|Accelerate to4673. Keep running while x<=4670.|
|122–154|right_run_jump|Full ascent; reach4766 with feet75.|
|154–166|right_run|Descend into axe trigger. End at4805 with flag_get=true and terminated=true.|

No extra60-frame settling wait is present: this branch uses the actual r59 arrival phase. Fresh model reproduction is still required and is owned by the main8-4 worker.

Evidence: `final-bowser-phase-diagnostic.json` (8 branches); `final-bowser-success-verification.json` (independent repeated successful branch); corresponding source scripts; `diagnostic-final-axe.jsonl` (explicit fresh_start=false / offline_diagnostic_only=true); `diagnostic-final-axe.verification.txt` (exact replay completed=True).
