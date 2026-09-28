# Stage 3-3: offline reflection history

Each attempt is a fresh AMD simulation with DJev choosing every live action. GPT edits stored questions between attempts. Regional lessons are stage-specific coaching, not a zero-shot policy. Derived terrain uses explicitly enabled observed tile IDs where needed.

| Attempt | Profile | Max x | Completed | Stop |
|---|---|---:|---|---|
| 001-stage-3-3-r01 | 3-3-r01-hazards | 456 | False | terminated |
| 002-stage-3-3-r02 | 3-3-r02-motion-jumps | 412 | False | terminated |
| 003-stage-3-3-r03 | 3-3-r03-short-hop | 314 | False | terminated |
| 004-stage-3-3-r04 | 3-3-r04-medium-hop | 415 | False | terminated |
| 005-stage-3-3-r05 | 3-3-r05-standalone-notes | 776 | False | terminated |
| 006-stage-3-3-r06 | 3-3-r06-reflection | 1818 | False | terminated |
| 007-stage-3-3-r07 | 3-3-r07-local-maneuver | 1980 | False | terminated |
| 008-stage-3-3-r08 | 3-3-r08-landing-reflection | 1968 | False | terminated |

## 001-stage-3-3-r01

Reflected instructions retained in the immutable profile:
```json
[]
```

## 003-stage-3-3-r03

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 235,
    "max_x": 315,
    "instructions": "OVERRIDE: Is Mario grounded? Answer from the grounded field only.",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false: release jump."
    }
  }
]
```

## 004-stage-3-3-r04

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 235,
    "max_x": 315,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least12."
    }
  }
]
```

## 005-stage-3-3-r05

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 235,
    "max_x": 315,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least12."
    },
    "replace_instructions": true
  }
]
```

## 006-stage-3-3-r06

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 235,
    "max_x": 315,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least12."
    },
    "replace_instructions": true
  },
  {
    "id": "land-before-upper-step",
    "min_x": 630,
    "max_x": 715,
    "replace_instructions": true,
    "instructions": "Is Mario grounded OR jump_elapsed_frames less than 12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than 12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least 12."
    }
  }
]
```

## 007-stage-3-3-r07

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 235,
    "max_x": 315,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least12."
    },
    "replace_instructions": true
  },
  {
    "id": "land-before-upper-step",
    "min_x": 630,
    "max_x": 715,
    "replace_instructions": true,
    "instructions": "Is Mario grounded OR jump_elapsed_frames less than 12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than 12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least 12."
    }
  },
  {
    "id": "hop-under-flying-koopa",
    "min_x": 1770,
    "max_x": 1860,
    "replace_instructions": true,
    "instructions": "Is Mario grounded?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false."
    }
  }
]
```

## 008-stage-3-3-r08

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 235,
    "max_x": 315,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least12."
    },
    "replace_instructions": true
  },
  {
    "id": "land-before-upper-step",
    "min_x": 630,
    "max_x": 715,
    "replace_instructions": true,
    "instructions": "Is Mario grounded OR jump_elapsed_frames less than 12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than 12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least 12."
    }
  },
  {
    "id": "hop-under-flying-koopa",
    "min_x": 1770,
    "max_x": 1860,
    "replace_instructions": true,
    "instructions": "Is Mario grounded?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false."
    }
  },
  {
    "id": "later-cluster-jump",
    "min_x": 1855,
    "max_x": 1883,
    "replace_instructions": true,
    "instructions": "Is x less than 1884?",
    "criteria": {
      "right_run": "Yes, x is less than 1884.",
      "right_run_jump": "No, x is at least 1884."
    }
  }
]
```


## Verified result

Verified treetop tiles [22,23,24] restored platform geometry. On the final moving lift, run until x2092 before jumping; jumping immediately from near rest capped air speed too low to reach the next platform. Exact replay passed. Winner and runtime metadata uploaded AMD. See `deliverables/stages/3-3/result.json` and `first-win.mp4`.


## Final attempt ledger

| Attempt/profile | Maximum x | Completed | Stop reason |
|---|---:|---|---|
| 001-stage-3-3-r01 | 456 | False | terminated |
| 002-stage-3-3-r02 | 412 | False | terminated |
| 003-stage-3-3-r03 | 314 | False | terminated |
| 004-stage-3-3-r04 | 415 | False | terminated |
| 005-stage-3-3-r05 | 776 | False | terminated |
| 006-stage-3-3-r06 | 1818 | False | terminated |
| 007-stage-3-3-r07 | 1980 | False | terminated |
| 008-stage-3-3-r08 | 1968 | False | terminated |
| 009-stage-3-3-r09 | 2219 | False | terminated |
| 010-stage-3-3-r10 | 2409 | True | completed |
