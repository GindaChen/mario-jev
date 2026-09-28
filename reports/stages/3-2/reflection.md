# Stage 3-2: offline reflection history

Each attempt is a fresh AMD simulation with DJev choosing every live action. GPT edits stored questions between attempts. Regional lessons are stage-specific coaching, not a zero-shot policy. Derived terrain uses explicitly enabled observed tile IDs where needed.

| Attempt | Profile | Max x | Completed | Stop |
|---|---|---:|---|---|
| 001-stage-3-2-r01 | 3-2-r01-hazards | 357 | False | terminated |
| 002-stage-3-2-r02 | 3-2-r02-motion-jumps | 1016 | False | terminated |
| 003-stage-3-2-r03 | 3-2-r03-reflect-first-failure | 946 | False | stalled |
| 004-stage-3-2-r04 | 3-2-r04-reflection | 2015 | False | terminated |
| 005-stage-3-2-r05 | 3-2-r05-standalone-notes | 1001 | False | terminated |
| 006-stage-3-2-r06 | 3-2-r06-reflection | 2108 | False | terminated |
| 007-stage-3-2-r07 | 3-2-r07-local-maneuver | 2070 | False | terminated |
| 008-stage-3-2-r08 | 3-2-r08-landing-reflection | 3337 | True | completed |

**Verified clear:** attempt 8, r08, exact replay passed. Shortened an early jump, delayed pit takeoff, then braked during descent to land before the second koopa. Video and runtime metadata are in deliverables/stages/3-2.

## 001-stage-3-2-r01

Reflected instructions retained in the immutable profile:
```json
[]
```

## 003-stage-3-2-r03

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "shorten-before-enemies",
    "min_x": 860,
    "max_x": 965,
    "instructions": "OVERRIDE: Is Mario grounded? Answer only from the grounded field.",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false: release jump."
    }
  }
]
```

## 004-stage-3-2-r04

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "shorten-before-enemies",
    "min_x": 860,
    "max_x": 915,
    "instructions": "OVERRIDE: Is Mario grounded? Answer only from the grounded field.",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false: release jump."
    }
  }
]
```

## 005-stage-3-2-r05

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "shorten-before-enemies",
    "min_x": 860,
    "max_x": 915,
    "instructions": "OVERRIDE: Is Mario grounded? Answer only from the grounded field.",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false: release jump."
    },
    "replace_instructions": true
  },
  {
    "id": "pit-late-takeoff",
    "min_x": 1820,
    "max_x": 1890,
    "instructions": "OVERRIDE: Is x less than 1891?",
    "criteria": {
      "right_run": "Yes, x is less than 1891.",
      "right_run_jump": "No, x is 1891 or higher."
    },
    "replace_instructions": true
  }
]
```

## 006-stage-3-2-r06

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "shorten-before-enemies",
    "min_x": 860,
    "max_x": 915,
    "instructions": "OVERRIDE: Is Mario grounded? Answer only from the grounded field.",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false: release jump."
    }
  },
  {
    "id": "pit-late-takeoff",
    "min_x": 1820,
    "max_x": 1890,
    "instructions": "OVERRIDE: Is x less than 1891?",
    "criteria": {
      "right_run": "Yes, x is less than 1891.",
      "right_run_jump": "No, x is 1891 or higher."
    },
    "replace_instructions": true
  }
]
```

## 007-stage-3-2-r07

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "shorten-before-enemies",
    "min_x": 860,
    "max_x": 915,
    "instructions": "OVERRIDE: Is Mario grounded? Answer only from the grounded field.",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false: release jump."
    }
  },
  {
    "id": "pit-late-takeoff",
    "min_x": 1820,
    "max_x": 1890,
    "instructions": "OVERRIDE: Is x less than 1891?",
    "criteria": {
      "right_run": "Yes, x is less than 1891.",
      "right_run_jump": "No, x is 1891 or higher."
    },
    "replace_instructions": true
  },
  {
    "id": "land-before-second-koopa",
    "min_x": 1950,
    "max_x": 2040,
    "replace_instructions": true,
    "instructions": "Is Mario grounded OR jump_elapsed_frames less than 12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than 12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least 12."
    }
  }
]
```

## 008-stage-3-2-r08

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "shorten-before-enemies",
    "min_x": 860,
    "max_x": 915,
    "instructions": "OVERRIDE: Is Mario grounded? Answer only from the grounded field.",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false: release jump."
    }
  },
  {
    "id": "pit-late-takeoff",
    "min_x": 1820,
    "max_x": 1890,
    "instructions": "OVERRIDE: Is x less than 1891?",
    "criteria": {
      "right_run": "Yes, x is less than 1891.",
      "right_run_jump": "No, x is 1891 or higher."
    },
    "replace_instructions": true
  },
  {
    "id": "brake-before-second-koopa",
    "min_x": 2030,
    "max_x": 2115,
    "replace_instructions": true,
    "instructions": "Is Mario falling?",
    "criteria": {
      "left": "Yes, motion is falling.",
      "right_run_jump": "No, motion is grounded or rising or airborne."
    }
  }
]
```


## Verified result

A shorter early hop and delayed pit takeoff fixed first obstacles. Near x2030–2115, choosing left only while falling positioned the landing before the second koopa, permitting another jump. Exact replay passed. Winner and runtime metadata uploaded AMD. See `deliverables/stages/3-2/result.json` and `first-win.mp4`.


## Final attempt ledger

| Attempt/profile | Maximum x | Completed | Stop reason |
|---|---:|---|---|
| 001-stage-3-2-r01 | 357 | False | terminated |
| 002-stage-3-2-r02 | 1016 | False | terminated |
| 003-stage-3-2-r03 | 946 | False | stalled |
| 004-stage-3-2-r04 | 2015 | False | terminated |
| 005-stage-3-2-r05 | 1001 | False | terminated |
| 006-stage-3-2-r06 | 2108 | False | terminated |
| 007-stage-3-2-r07 | 2070 | False | terminated |
| 008-stage-3-2-r08 | 3337 | True | completed |
