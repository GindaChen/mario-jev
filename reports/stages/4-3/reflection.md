# Stage 4-3: offline reflection history

Each attempt is a fresh AMD simulation with DJev choosing every live action. GPT edits stored questions between attempts. Regional lessons are stage-specific coaching, not a zero-shot policy. Derived terrain uses explicitly enabled observed tile IDs where needed.

| Attempt | Profile | Max x | Completed | Stop |
|---|---|---:|---|---|
| 001-stage-4-3-r01 | 4-3-r01-hazards | 399 | False | terminated |
| 002-stage-4-3-r02 | 4-3-r02-motion-jumps | 593 | False | terminated |
| 003-stage-4-3-r03 | 4-3-r03-short-hop | 410 | False | terminated |
| 004-stage-4-3-r04 | 4-3-r04-medium-hop | 840 | False | terminated |
| 005-stage-4-3-r05 | 4-3-r05-standalone-notes | 840 | False | terminated |
| 006-stage-4-3-r06 | 4-3-r06-reflection | 1320 | False | terminated |
| 007-stage-4-3-r07 | 4-3-r07-local-maneuver | 1197 | False | terminated |
| 008-stage-4-3-r08 | 4-3-r08-land-earlier | 1320 | False | terminated |

## 001-stage-4-3-r01

Reflected instructions retained in the immutable profile:
```json
[]
```

## 003-stage-4-3-r03

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 355,
    "max_x": 445,
    "instructions": "OVERRIDE: Is Mario grounded? Answer from the grounded field only.",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false: release jump."
    }
  }
]
```

## 004-stage-4-3-r04

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 355,
    "max_x": 445,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least12."
    }
  }
]
```

## 005-stage-4-3-r05

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 355,
    "max_x": 445,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least12."
    },
    "replace_instructions": true
  }
]
```

## 006-stage-4-3-r06

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 355,
    "max_x": 445,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least12."
    },
    "replace_instructions": true
  },
  {
    "id": "land-before-upper-step",
    "min_x": 639,
    "max_x": 730,
    "replace_instructions": true,
    "instructions": "Is Mario grounded OR jump_elapsed_frames less than 12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than 12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least 12."
    }
  }
]
```

## 007-stage-4-3-r07

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 355,
    "max_x": 445,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least12."
    },
    "replace_instructions": true
  },
  {
    "id": "land-before-upper-step",
    "min_x": 639,
    "max_x": 730,
    "replace_instructions": true,
    "instructions": "Is Mario grounded OR jump_elapsed_frames less than 12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than 12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least 12."
    }
  },
  {
    "id": "step-approach",
    "min_x": 1140,
    "max_x": 1153,
    "replace_instructions": true,
    "instructions": "Is Mario falling?",
    "criteria": {
      "right_run": "Yes, motion is falling.",
      "right_run_jump": "No, motion is grounded or rising or airborne."
    }
  },
  {
    "id": "step-center",
    "min_x": 1154,
    "max_x": 1160,
    "replace_instructions": true,
    "instructions": "Is feet_y less than 80?",
    "criteria": {
      "right_run_jump": "Yes, feet_y is less than 80.",
      "jump": "No, feet_y is at least 80."
    }
  },
  {
    "id": "step-return",
    "min_x": 1161,
    "max_x": 1220,
    "replace_instructions": true,
    "instructions": "Is feet_y less than 80?",
    "criteria": {
      "right_run_jump": "Yes, feet_y is less than 80.",
      "left_jump": "No, feet_y is at least 80."
    }
  }
]
```

## 008-stage-4-3-r08

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 355,
    "max_x": 445,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least12."
    },
    "replace_instructions": true
  },
  {
    "id": "land-before-upper-step",
    "min_x": 639,
    "max_x": 730,
    "replace_instructions": true,
    "instructions": "Is Mario grounded OR jump_elapsed_frames less than 12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than 12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least 12."
    }
  },
  {
    "id": "land-before-tall-step",
    "min_x": 1040,
    "max_x": 1140,
    "replace_instructions": true,
    "instructions": "Have at least 28 frames elapsed in land-before-tall-step?",
    "criteria": {
      "left_jump": "No, fewer than 28 frames elapsed: brake left while holding jump.",
      "right_run_jump": "Yes, at least 28 frames elapsed: move right holding jump."
    }
  }
]
```


## Verified result

Verified mushroom tiles [25,26,27] restored geometry. Shorten preceding jump in x980–1080 to 8 frames held: this lands early before the tall step1120. Braking after reaching its underside did not fix the low takeoff origin. Exact replay passed. Winner and runtime metadata uploaded AMD. See `deliverables/stages/4-3/result.json` and `first-win.mp4`.


## Final attempt ledger

| Attempt/profile | Maximum x | Completed | Stop reason |
|---|---:|---|---|
| 001-stage-4-3-r01 | 399 | False | terminated |
| 002-stage-4-3-r02 | 593 | False | terminated |
| 003-stage-4-3-r03 | 410 | False | terminated |
| 004-stage-4-3-r04 | 840 | False | terminated |
| 005-stage-4-3-r05 | 840 | False | terminated |
| 006-stage-4-3-r06 | 1320 | False | terminated |
| 007-stage-4-3-r07 | 1197 | False | terminated |
| 008-stage-4-3-r08 | 1320 | False | terminated |
| 009-stage-4-3-r09 | 1166 | False | terminated |
| 010-stage-4-3-r10 | 2345 | True | completed |
