# 6-2 campaign: first divergent request audit

## Finding

The first action difference is decision 196 at x=1141. The historical winning trace and campaign attempts 1, 2, and 3 have identical request dictionaries through that decision. Their compact JSON serialization also matches exactly. The first request difference appears at decision 197, after the different action has already changed the state/history.

This is not a discrepancy in the logged timer or observation. The same request receives a different historical versus current model choice. The precise serving-side cause is not established by this read-only comparison.

## Evidence

Historical winner: `deliverables/stages/6-2/winning-trace.jsonl`, originating from `runs/stages/6-2/batches/043-stage-6-2-r27/20260928T060528104847Z.jsonl`.

Campaign: AMD `runs/overnight-campaign/trajectory.jsonl`, stage `6-2`, attempts 1–3, decision 196. Attempt 1 is sequence 10692. The frozen profile digest is `baabc323d83cec728da8025aebb48a4c14ea7ba6cc82e8d735fe74191fbfca77`.

Request digest at decision 196, computed using `json.dumps(request, separators=(',', ':'))` in recorded key order:

`d33b19fce410b098c377837f4ff2ec6501381ea9018629fb827ae8f826ac0607`

The matching state includes x=1141, feet_y=200, grounded=false, motion=falling, horizontal_speed=2.5, jump_elapsed_frames=48, last_action=left, and `note_elapsed_frames.pipe-cluster-phase=12`. Inference is samples=1, seed=0, steps=1.

The exact action question is:

```json
{
  "instructions": "Use pipe-cluster-phase elapsed frames. Brake left for20 frames. Wait until120 frames. Then jump right.",
  "criteria": {
    "left": "Elapsed less than20.",
    "wait": "Elapsed at least20 and less than120.",
    "right_run_jump": "Elapsed at least120."
  }
}
```

| Trace | Endpoint | Selected | P(left) | P(wait) |
|---|---|---|---:|---:|
| Historical winner | 18517 | wait | 0.234023925 | 0.765967638 |
| Campaign attempt 1 | 18515 | left | 0.499993488 | 0.499993488 |
| Campaign attempt 2 | 18516 | left | 0.499993488 | 0.499993488 |
| Campaign attempt 3 | 18517 | left | 0.499993488 | 0.499993488 |

Thus switching back to the historical endpoint did not recover the historical choice in these observed runs. The historical winner also chose wait at elapsed=0, contrary to the stated brake-before-20 rule; all three campaign attempts reproduced that earlier wait.

Both decision-196 actions execute two frames because Mario lands. At decision 197 both traces show x=1145, feet_y=208, grounded=true, and the same coarse horizontal-speed estimate of 2.0. However, raw horizontal velocity differs (winner 34, campaign 33), and previous action differs. The winner reaches x=1153 at decision 198 and rests at x=1158; the failing branch reaches x=1152 and rests at x=1155. The subtle initial change therefore alters the subsequent takeoff position.

## Recommendation sent to the editing agent

Clarifying the original arithmetic to force left whenever elapsed<20 would enforce the failing decision at elapsed=12. For a minimal attempt to recover the historical trajectory, retain the historical profile and append a higher-priority note limited to x=1140..1144 with `replace_instructions:true`:

- Question: "Is Mario falling? Release horizontal controls during the final landing; otherwise brake left."
- `wait`: "Yes, motion is falling."
- `left`: "No, motion is grounded or rising."

This changes only the identified landing decision on the observed trajectory. The existing pipe-cluster note remains active and its timer continues accumulating. After the two-frame landing, x=1145 leaves the narrow override and returns to the original timer at 14 frames. Restoring that action should restore the recorded physical branch up to any later inference difference; a new successful run is still required. This is a proposed model-choice prompt, not a scripted action replacement.

The profile-editing agent owns deployment and validation and has staged this as an alternative to its broader drop-to-step fix. This audit changed no profiles or controller source and ran no gameplay or model requests.

## Subsequent live validation

The editing agent deployed the focused candidate as campaign attempt 6 (`profiles/6-2-006.json`, SHA-256 `7a9e11797e47b0342ed43163a163e8caf76d6bb336c1cc01729731d0e90cc208`, endpoint 18516). Read-only inspection confirms decision 196 now selects wait with probability 0.998581916 and executes the two-frame landing. Sequence 14215 records the actual stage clear at 2026-09-28 08:14:06 UTC.

A complete comparison of all 518 decisions in campaign attempt 6 against the historical winning trace finds zero action/frame-count differences and zero Mario-state differences. The narrow prompt successfully recovered the entire historical physical trajectory in this live model-controlled attempt. This establishes this attempt's success, not a general reliability estimate.
