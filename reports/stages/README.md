# Independent stage campaign

Goal: clear all original Super Mario Bros. stages independently, with four parallel AMD workers using AMD-local DJev and offline GPT reflection. A stage passes only when a fresh run has an explicit `completed: true` summary and its recorded actions replay exactly. After the first verified clear, retain the prompt, runtime metadata and video, and advance to another unpassed stage. World-skipping warp optimization is deferred; normal internal pipe traversal is allowed.

Prior results: 1-1 passed in the earlier comparison; 1-2 passed in the closed 100-run reflection experiment; 1-3 passed in the 31-run stage experiment. The new campaign resumes at 1-4. `status.json` combines per-stage run folders with verified historical evidence. 1-1 is the prior B200 DJev baseline with a replay but no immutable prompt snapshot; 1-2 is the closed AMD 100-run study. Their original datasets remain unchanged.

Each stage uses `runs/stages/W-S` (usually its `batches` subfolder) with immutable per-attempt profiles and source snapshots. Candidate prompts live in `prompts/stages/W-S`; `winner.json` is written only after a fresh completed run replays exactly. `deliverables/stages/W-S` retains the winner trace, profile, result, replay verification, and video. Reflection notes live beside this report.

This is stage-specific coaching with unchanged model weights. Emulator time pauses during inference. Completion of each stage independently is distinct from an uninterrupted full-game run.

AMD fresh-game command for stages with a frozen prompt/runtime (1-1 is playback-only historical evidence): `scripts/run_amd_stage.sh W S`.
