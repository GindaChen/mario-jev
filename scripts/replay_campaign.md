# Campaign replay exports

Run against a completed, stable trajectory. Both video modes replay and verify **every recorded decision**, including failed attempts. A divergence in an omitted attempt still fails winning-only export. Without `--allow-incomplete`, all 32 ordered clears and the campaign completion event are required.

```sh
.venv/bin/python scripts/replay_campaign.py PATH/trajectory.jsonl --video full-attempts.mp4
.venv/bin/python scripts/replay_campaign.py PATH/trajectory.jsonl --video winning-stages.mp4 --winning-only
```

The chronological video is labeled `Chronological | ALL ATTEMPTS`. The winning-only video is labeled `Winning stages | STITCHED` on every frame and includes only the first cleared attempt for each stage. Stage cards retain the original attempt number. Winning-only playback is an edited presentation, not evidence of an uninterrupted successful run. Neither mode includes model inference waiting time or emulator-skipped cutscene frames.

The final JSON separates:

- `environment_loads`: every recorded reset/load, including an unfinished load at the trace tail.
- `stage_loads`: normal explicit stage loads, including the initial load. Natural transitions are reported separately as `natural_stage_transitions`.
- `retries`: loads associated with a repeated-stage or attempt-number-greater-than-one `stage_start`; normal next-stage loads do not increase this count.
- `unclassified_loads`: resets without a following `stage_start`, normally possible only in incomplete traces.
- `video_mode` and `video_frames`: which presentation was produced and its encoded frame count. `decisions` always counts every verified decision, regardless of presentation.

Reset reasons alone are insufficient because the campaign uses `explicit_stage_loader` both after failure and after a normal clear. Classification therefore uses the following `stage_start` event and prior stage/attempt history. A failed attempt at the end of an incomplete trace is not counted as a retry until another attempt actually starts.

Existing output files are never overwritten (`ffmpeg -n`). No exports are triggered by editing or testing the script.
