# What this experiment demonstrates

The target is an independent clear of each Super Mario Bros. stage. Every episode resets directly into its designated stage. A completed campaign is not evidence of one uninterrupted 1-1 through 8-4 playthrough, nor of generalization to unseen games or seeds.

## Execution and reflection

- Gameplay simulation and DJev inference for the new campaign run on AMD. Four replicas use physical GPUs 4, 5, 6 and 7; the deployment and measured PCI/HIP mapping are in `parallel-services.md`.
- Each worker runs a fresh episode, examines the recorded failure, writes a versioned prompt revision, and retries. Runtime cutoffs are recorded separately from in-game deaths; for example, 8-4 required a longer stall allowance when an internal room reset its horizontal coordinate. Independent stages and small candidate batches run concurrently.
- GPT agents perform offline reflection. They inspect positions, terrain, enemy timing and actual model requests/responses; some hard maneuvers also use clearly labeled replay-prefix physics probes. Such probes are diagnostics, excluded from model-run success claims.
- The final8-4 winner also uses a DJev instruction selector before some action queries. Selected instructions can expose only relevant observation fields. Both selection and action calls are logged; no router is retroactively inferred for earlier stages.
- DJev selects the actions in every reported fresh campaign clear. There are no replayed action prefixes in those runs. Model weights are unchanged.
- Coaching is explicitly stage-specific: geographic activation ranges, elapsed-frame instructions, desired jump lengths, waits and pipe alignment. This is substantial engineered assistance, not a claim that the base model solved the game unaided.
- The harness changed during development: opt-in terrain recognition, room metadata and room-scoped notes, local instruction replacement, observed-landmark activation of instruction timers, and an explicit down action support difficult stages. Manifest-backed per-attempt source/profile snapshots distinguish these versions. The integrity audit also explicitly lists two early 1-3 pilot traces that have no reservation manifest; their source snapshots must not be inferred. Default observations and actions are not retroactively changed in archived runs.
- The emulator pauses while inference is pending. Replay videos show simulation frames, not inference wall-clock delay. This campaign does not test asynchronous System 1/System 2 play in real time.

## Pass rule and evidence

A new campaign pass requires a fresh-start trace with `completed: true`, followed by an exact action replay from reset. The replay checks recorded positions and actual completion. Progress distance alone, reaching a pipe, or clearing a diagnostic branch is insufficient. The first verified winner is retained; no extra confirmation trials are requested after a clear. Already-running parallel candidates may also finish.

Every stage has a replay video and provenance/result record once verified. Modern campaign winners also retain the exact profile and runtime settings. Failed trials, API failures, profile snapshots, source snapshots, raw model queries and responses remain in the run folders and manifests. Reports distinguish the proposed maneuver from the actions actually executed: a prompt edit that produces the same actions is not an effective experimental intervention.

Normal stage-internal pipe traversal is allowed. World-skipping warp optimization is deferred. Some maze analysis uses the saved primary SMB disassembly and a cited walkthrough; stage reports identify these inputs. No ROM or RAM state is edited to achieve a clear.

## Historical evidence

1-1 is an earlier B200 BF16 DJev clear, now replay-verified again. Its old trace has no immutable prompt/source snapshot, so the normalized artifact is explicitly playback-only rather than a fabricated reproducible AMD deployment. 1-2 is the closed 100-attempt AMD reflection study (24 completed runs, including its separate validation and ablation phases). 1-3 is the prior 31-attempt stage study. These datasets are preserved and identified separately from this parallel campaign.

## Reading the audit

Start with `progress.md`. `attempt-audit.json` checks reservation accounting, profile hashes, archived source-content hashes and per-decision profile identity; infrastructure errors and unfinished traces remain visible. For one stage, open `reports/stages/W-S/reflection.md`, compare candidate JSON files in `prompts/stages/W-S`, and inspect the corresponding attempt folder in `runs/stages/W-S`. The normalized winner bundle is `deliverables/stages/W-S`. The logs expose observations, prompts, model outputs, selected actions and experiment decisions; they do not claim to reveal a model's private internal reasoning.
