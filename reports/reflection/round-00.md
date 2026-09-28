# Reflection before trials 1-4

Source: prior DJev traces19-d1 and28-d9, plus hosted trace16-v16 as an explicitly disclosed historical failure observation (no hosted calls in this experiment).

- d9 decisions151-157: retreat anchored to airborne feet126, so feet142 incorrectly counted as16px below a support that was actually144. Anchor to last grounded support.
- d9 decisions245-248: falling enemies excluded by same-height filter until nearly touching. Show all nearby objects and choose joint movement/jump.
- d1 decisions189-197: first pit jump35px early under ceiling32, lands below far bank. Test later takeoff.
- Contradictory independent jump votes can defeat correct retreat instructions. Replace them with one model-selected complete action.

First batch compares a unified action question, retrieved stage lessons, four inference steps, and128-token DJev thinking. All are fresh AMD-local DJev trials. No replay prefix is supplied. Geographic notes are intentionally stage-specific. These comparisons are exploratory, not statistically powered.
