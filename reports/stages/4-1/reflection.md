# Stage 4-1: offline reflection history

Each attempt is a fresh AMD simulation with DJev choosing every live action. GPT edits stored questions between attempts. Regional lessons are stage-specific coaching, not a zero-shot policy. Derived terrain uses explicitly enabled observed tile IDs where needed.

| Attempt | Profile | Max x | Completed | Stop |
|---|---|---:|---|---|
| 001-stage-4-1-r01 | 4-1-r01-hazards | 1857 | False | terminated |
| 002-stage-4-1-r02 | 4-1-r02-motion-jumps | 1316 | False | terminated |
| 003-stage-4-1-r03 | 4-1-r03-reflect-first-failure | 1859 | False | terminated |
| 004-stage-4-1-r04 | 4-1-r04-reflection | 1857 | False | terminated |
| 005-stage-4-1-r05 | 4-1-r05-standalone-notes | 2122 | False | terminated |
| 006-stage-4-1-r06 | 4-1-r06-reflection | 2122 | False | terminated |
| 007-stage-4-1-r07 | 4-1-r07-local-maneuver | 2115 | False | terminated |
| 008-stage-4-1-r08 | 4-1-r08-landing-reflection | 2127 | False | terminated |

## 001-stage-4-1-r01

Reflected instructions retained in the immutable profile:
```json
[]
```

## 003-stage-4-1-r03

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "pipe-timing",
    "min_x": 1750,
    "max_x": 1820,
    "instructions": "OVERRIDE: Has note_elapsed_frames.pipe-timing reached60?",
    "criteria": {
      "wait": "No, elapsed is less than60.",
      "right_run_jump": "Yes, elapsed is at least60."
    }
  }
]
```

## 004-stage-4-1-r04

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "plant-cycle",
    "min_x": 1650,
    "max_x": 1740,
    "instructions": "OVERRIDE: Is note_elapsed_frames.plant-cycle less than180?",
    "criteria": {
      "wait": "Yes, elapsed is less than180.",
      "right_run": "No, elapsed is180orhigher."
    }
  }
]
```

## 005-stage-4-1-r05

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "pipe-early-takeoff",
    "min_x": 1760,
    "max_x": 1920,
    "instructions": "OVERRIDE: Is Mario falling? Answer using the motion field only.",
    "criteria": {
      "right_run": "Yes, motion is falling.",
      "right_run_jump": "No, motion is grounded or rising or airborne."
    },
    "replace_instructions": true
  }
]
```

## 006-stage-4-1-r06

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "pipe-early-takeoff",
    "min_x": 1760,
    "max_x": 1920,
    "instructions": "OVERRIDE: Is Mario falling? Answer using the motion field only.",
    "criteria": {
      "right_run": "Yes, motion is falling.",
      "right_run_jump": "No, motion is grounded or rising or airborne."
    },
    "replace_instructions": true
  },
  {
    "id": "second-pipe-early",
    "min_x": 1980,
    "max_x": 2160,
    "replace_instructions": true,
    "instructions": "Is Mario falling? Answer using the motion field only.",
    "criteria": {
      "right_run": "Yes, motion is falling.",
      "right_run_jump": "No, motion is grounded or rising or airborne."
    }
  }
]
```

## 007-stage-4-1-r07

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "pipe-early-takeoff",
    "min_x": 1760,
    "max_x": 1920,
    "instructions": "OVERRIDE: Is Mario falling? Answer using the motion field only.",
    "criteria": {
      "right_run": "Yes, motion is falling.",
      "right_run_jump": "No, motion is grounded or rising or airborne."
    },
    "replace_instructions": true
  },
  {
    "id": "second-pipe-early",
    "min_x": 1980,
    "max_x": 2160,
    "replace_instructions": true,
    "instructions": "Is Mario falling? Answer using the motion field only.",
    "criteria": {
      "right_run": "Yes, motion is falling.",
      "right_run_jump": "No, motion is grounded or rising or airborne."
    }
  },
  {
    "id": "land-early-second-pipe",
    "min_x": 1950,
    "max_x": 2030,
    "replace_instructions": true,
    "instructions": "Is Mario grounded OR jump_elapsed_frames less than 12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than 12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least 12."
    }
  }
]
```

## 008-stage-4-1-r08

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "pipe-early-takeoff",
    "min_x": 1760,
    "max_x": 1920,
    "instructions": "OVERRIDE: Is Mario falling? Answer using the motion field only.",
    "criteria": {
      "right_run": "Yes, motion is falling.",
      "right_run_jump": "No, motion is grounded or rising or airborne."
    },
    "replace_instructions": true
  },
  {
    "id": "second-pipe-early",
    "min_x": 1980,
    "max_x": 2160,
    "replace_instructions": true,
    "instructions": "Is Mario falling? Answer using the motion field only.",
    "criteria": {
      "right_run": "Yes, motion is falling.",
      "right_run_jump": "No, motion is grounded or rising or airborne."
    }
  },
  {
    "id": "land-early-second-pipe",
    "min_x": 1870,
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


## Verified result

Verified first clear: attempt11 r11, exact replay passed. The final double gap required a medium 12-frame held jump from2740–2860 to land on the island2832–2880 before jumping again. Winner and runtime metadata uploaded AMD. Video deliverables/stages/4-1/first-win.mp4.


## Final attempt ledger

| Attempt/profile | Maximum x | Completed | Stop reason |
|---|---:|---|---|
| 001-stage-4-1-r01 | 1857 | False | terminated |
| 002-stage-4-1-r02 | 1316 | False | terminated |
| 003-stage-4-1-r03 | 1859 | False | terminated |
| 004-stage-4-1-r04 | 1857 | False | terminated |
| 005-stage-4-1-r05 | 2122 | False | terminated |
| 006-stage-4-1-r06 | 2122 | False | terminated |
| 007-stage-4-1-r07 | 2115 | False | terminated |
| 008-stage-4-1-r08 | 2127 | False | terminated |
| 009-stage-4-1-r09 | 2407 | False | terminated |
| 010-stage-4-1-r10 | 2906 | False | terminated |
| 011-stage-4-1-r11 | 3593 | True | completed |
