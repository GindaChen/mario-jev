# Stage 3-1: offline reflection history

Each attempt is a fresh AMD simulation with DJev choosing every live action. GPT edits stored questions between attempts. Regional lessons are stage-specific coaching, not a zero-shot policy. Derived terrain uses explicitly enabled observed tile IDs where needed.

| Attempt | Profile | Max x | Completed | Stop |
|---|---|---:|---|---|
| 001-stage-3-1-r01 | 3-1-r01-hazards | 1086 | False | terminated |
| 002-stage-3-1-r02 | 3-1-r02-motion-jumps | 1284 | False | terminated |
| 003-stage-3-1-r03 | 3-1-r03-reflect-first-failure | 1399 | False | terminated |
| 004-stage-3-1-r04 | 3-1-r04-reflection | 1399 | False | terminated |
| 005-stage-3-1-r05 | 3-1-r05-standalone-notes | 1856 | False | terminated |
| 006-stage-3-1-r06 | 3-1-r06-reflection | 1634 | False | terminated |
| 007-stage-3-1-r07 | 3-1-r07-local-maneuver | 3010 | False | terminated |
| 008-stage-3-1-r08 | 3-1-r08-landing-reflection | 3027 | False | terminated |

## 001-stage-3-1-r01

Reflected instructions retained in the immutable profile:
```json
[]
```

## 003-stage-3-1-r03

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "shorten-before-enemies",
    "min_x": 1150,
    "max_x": 1240,
    "instructions": "OVERRIDE: Is Mario grounded? Answer only from the grounded field.",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false: release jump."
    }
  }
]
```

## 004-stage-3-1-r04

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "shorten-before-enemies",
    "min_x": 1150,
    "max_x": 1240,
    "instructions": "OVERRIDE: Is Mario grounded? Answer only from the grounded field.",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false: release jump."
    }
  },
  {
    "id": "low-ceiling-pit",
    "min_x": 1320,
    "max_x": 1470,
    "instructions": "OVERRIDE: Is Mario grounded?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false."
    }
  }
]
```

## 005-stage-3-1-r05

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "shorten-before-enemies",
    "min_x": 1150,
    "max_x": 1240,
    "instructions": "OVERRIDE: Is Mario grounded? Answer only from the grounded field.",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false: release jump."
    },
    "replace_instructions": true
  },
  {
    "id": "land-before-bridge-gap",
    "min_x": 1240,
    "max_x": 1340,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than 12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than 12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least 12."
    },
    "replace_instructions": true
  }
]
```

## 006-stage-3-1-r06

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "shorten-before-enemies",
    "min_x": 1150,
    "max_x": 1240,
    "instructions": "OVERRIDE: Is Mario grounded? Answer only from the grounded field.",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false: release jump."
    },
    "replace_instructions": true
  },
  {
    "id": "land-before-bridge-gap",
    "min_x": 1240,
    "max_x": 1340,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than 12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than 12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least 12."
    },
    "replace_instructions": true
  },
  {
    "id": "stay-below-hammers",
    "min_x": 1600,
    "max_x": 1765,
    "replace_instructions": true,
    "instructions": "Is x less than 1766?",
    "criteria": {
      "right_run": "Yes, x is less than 1766.",
      "right_run_jump": "No, x is at least 1766."
    }
  },
  {
    "id": "low-hammer-hops",
    "min_x": 1766,
    "max_x": 1920,
    "replace_instructions": true,
    "instructions": "Is Mario grounded?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false."
    }
  }
]
```

## 007-stage-3-1-r07

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "shorten-before-enemies",
    "min_x": 1150,
    "max_x": 1240,
    "instructions": "OVERRIDE: Is Mario grounded? Answer only from the grounded field.",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false: release jump."
    },
    "replace_instructions": true
  },
  {
    "id": "land-before-bridge-gap",
    "min_x": 1240,
    "max_x": 1340,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than 12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than 12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least 12."
    },
    "replace_instructions": true
  },
  {
    "id": "stay-below-hammers",
    "min_x": 1670,
    "max_x": 1765,
    "replace_instructions": true,
    "instructions": "Is x less than 1766?",
    "criteria": {
      "right_run": "Yes, x is less than 1766.",
      "right_run_jump": "No, x is at least 1766."
    }
  },
  {
    "id": "low-hammer-hops",
    "min_x": 1766,
    "max_x": 1920,
    "replace_instructions": true,
    "instructions": "Is Mario grounded?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false."
    }
  }
]
```

## 008-stage-3-1-r08

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "shorten-before-enemies",
    "min_x": 1150,
    "max_x": 1240,
    "instructions": "OVERRIDE: Is Mario grounded? Answer only from the grounded field.",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false: release jump."
    },
    "replace_instructions": true
  },
  {
    "id": "land-before-bridge-gap",
    "min_x": 1240,
    "max_x": 1340,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than 12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than 12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least 12."
    },
    "replace_instructions": true
  },
  {
    "id": "stay-below-hammers",
    "min_x": 1670,
    "max_x": 1765,
    "replace_instructions": true,
    "instructions": "Is x less than 1766?",
    "criteria": {
      "right_run": "Yes, x is less than 1766.",
      "right_run_jump": "No, x is at least 1766."
    }
  },
  {
    "id": "low-hammer-hops",
    "min_x": 1766,
    "max_x": 1920,
    "replace_instructions": true,
    "instructions": "Is Mario grounded?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false."
    }
  },
  {
    "id": "land-before-final-stairs",
    "min_x": 2790,
    "max_x": 2880,
    "replace_instructions": true,
    "instructions": "Is Mario grounded OR jump_elapsed_frames less than 12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than 12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least 12."
    }
  }
]
```


## Verified result

The final staircase required braking left while holding jump for 24 frames in x2960–3050 before resuming right. This landed on the higher step before the upper koopa. Earlier hammer brothers were passed by low running followed by short hops. Exact replay passed. Winner and runtime metadata uploaded AMD. See `deliverables/stages/3-1/result.json` and `first-win.mp4`.


## Final attempt ledger

| Attempt/profile | Maximum x | Completed | Stop reason |
|---|---:|---|---|
| 001-stage-3-1-r01 | 1086 | False | terminated |
| 002-stage-3-1-r02 | 1284 | False | terminated |
| 003-stage-3-1-r03 | 1399 | False | terminated |
| 004-stage-3-1-r04 | 1399 | False | terminated |
| 005-stage-3-1-r05 | 1856 | False | terminated |
| 006-stage-3-1-r06 | 1634 | False | terminated |
| 007-stage-3-1-r07 | 3010 | False | terminated |
| 008-stage-3-1-r08 | 3027 | False | terminated |
| 009-stage-3-1-r09 | 2974 | False | terminated |
| 010-stage-3-1-r10 | 3193 | True | completed |
