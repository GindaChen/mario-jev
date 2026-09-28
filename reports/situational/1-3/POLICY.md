# Review: situation-based 1-3 policy

This is a new experiment on branch `situational-1-3`, based on merged PR #1. Earlier prompts, campaign traces, reports and videos are unchanged. These tests load stage 1-3 independently using the existing stage runner; they do not demonstrate native full-game transitions or a full-game win. The stage runner retains its existing animation shortcuts. Native full-game integration is a later evaluation step.

## Exact instruction text sent on every decision

Choose the controller action that makes safe progress toward the goal on the right. Infer the current situation from relative geometry and motion. Plan a landing, not just a takeoff: the feet must reach the top of a supported surface before descending below it. Running builds horizontal momentum; left can brake it. Holding jump while rising can increase height; pressing jump after falling cannot rescue a missed takeoff. Release jump before starting another jump. Compare current velocity, remaining platform length, target height, headroom and nearby enemies. Candidate surfaces are observations, not guarantees of reachability or safety. Empty floor underneath a platform does not mean the platform is absent. Unknown offscreen terrain is not confirmed support. Choose from the same action menu in every situation.

Stage guidance: Stage 1-3 is an elevated platform course. Choose a reachable next platform and control where you land. A higher landing needs enough ascent before its edge; a narrow landing may require braking to avoid overshooting. Reassess after touching down before launching the next jump. Flying enemies may cross the landing area: compare their relative height and distance with your path. Do not retreat automatically merely because an enemy is above you; preserve a supported landing. Use observed geometry rather than assuming every gap needs the same jump.

## What the model controls

One model request chooses from the same nine actions every time: wait, right, right+jump, right+run, right+run+jump, left, left+jump, jump, or down. The option descriptions describe buttons only; they do not encode situation-to-action rules. There is no model-independent instruction selector, coordinate gate, timed maneuver, route switch or action-menu replacement.

Requests contain grounded/motion state, measured horizontal and vertical speed, power state, whether jump is held, headroom, relative wall/gap distances, relative landing-surface extents and heights, relative object positions, the stage label and the action horizon. Absolute x/y, room identifiers and note timers are excluded from the request. Absolute positions remain in audit logs for diagnosing failures. A fixed four-frame decision horizon is execution granularity, not a maneuver schedule.

The approved jump-release helper is retained: when grounded with A already held, a selected jump action has A removed so another jump can be started. This uses one execution frame. Both selected and executed actions are recorded. No additional buttons are inserted after model selection.

## Perception revision, not a prompt revision

v1 omitted platform tiles 0x16–0x18 (decimal 22–24) from the landing-surface extractor. Its three attempts failed at max x=368, 287 and 287. Recorded terrain shows Mario standing at feet y=192 at a platform edge with tile 0x16 in row 10, while the extractor did not represent that platform as a candidate landing.

v2 supplies those three platform metatile IDs to the existing geometry extractor, only for this new profile. General guidance and stage guidance are byte-for-byte unchanged. This correction encodes what counts as platform geometry; it does not specify when to jump. Candidate surfaces are not predictions of safe or reachable landings. Unknown enemy types and approximate geometry remain limitations.

## Evaluation and review boundary

Both versions receive three bounded trials on the same local DJev endpoint, using seed 123 and the same starting state. Repeated trials are a smoke test, not evidence of generalization across different states. Profiles and source snapshots are retained separately for every batch; no successful old trajectory is credited here.

Before another prompt revision, review the guidance above and the exact request example beside this document. Future reflection should describe a reusable relationship between motion, support and landing geometry, without introducing exact level coordinates, note timers or forced action options.

## Initial results

| Version | Cleared | Maximum x per attempt |
| --- | --- | --- |
| v1 | 0 / 3 | 368, 287, 287 |
| v2 (platform perception corrected) | 0 / 3 | 385, 395, 395 |

All six runs ended without a clear. The fixed action menu and selected/executed action correspondence were checked across all recorded decisions; any differences were the approved jump-release helper. Raw traces are downloaded under `runs/situational/` in this checkout and remain on AMD in the isolated experiment folder. `results.json` records their hashes; `example-request.json` contains an actual v2 inference request. No replay verification or successful full-game evaluation is claimed for this batch.
