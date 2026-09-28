# Stage 3-4: offline reflection history

Each attempt is a fresh AMD simulation with DJev choosing every live action. GPT edits stored questions between attempts. Regional lessons are stage-specific coaching, not a zero-shot policy. Derived terrain uses explicitly enabled observed tile IDs where needed.

| Attempt | Profile | Max x | Completed | Stop |
|---|---|---:|---|---|
| 001-stage-3-4-r01 | 3-4-r01-hazards | 248 | False | terminated |
| 002-stage-3-4-r02 | 3-4-r02-motion-jumps | 417 | False | terminated |
| 003-stage-3-4-r03 | 3-4-r03-short-hop | 354 | False | terminated |
| 004-stage-3-4-r04 | 3-4-r04-medium-hop | 411 | False | terminated |
| 005-stage-3-4-r05 | 3-4-r05-standalone-notes | 411 | False | terminated |
| 006-stage-3-4-r06 | 3-4-r06-reflection | 408 | False | terminated |
| 007-stage-3-4-r07 | 3-4-r07-local-maneuver | 1544 | False | terminated |
| 008-stage-3-4-r08 | 3-4-r08-landing-reflection | 1525 | False | terminated |

## 001-stage-3-4-r01

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "lava-takeoff",
    "min_x": 340,
    "max_x": 420,
    "instructions": "Use the measured takeoff fact; approach this long lava gap before jumping.",
    "thresholds": {
      "pit": 0
    }
  },
  {
    "id": "fireball-clearance",
    "min_x": 1500,
    "max_x": 10000,
    "instructions": "Jump early enough to clear fast approaching fireballs.",
    "thresholds": {
      "enemy": 64
    }
  },
  {
    "id": "castle-step",
    "min_x": 1800,
    "max_x": 10000,
    "instructions": "OVERRIDE: jump onto the raised castle step ahead. If grounded or rising jump right. If falling run right without jump.",
    "criteria": {
      "right_run_jump": "Grounded or rising: jump right.",
      "right_run": "Falling: run right."
    }
  },
  {
    "id": "bowser-approach",
    "min_x": 2030,
    "max_x": 2100,
    "instructions": "OVERRIDE: approach Bowser before starting the final jump. Grounded or falling: run right without jump. Only if already rising sustain jump right.",
    "criteria": {
      "right_run": "Grounded or falling: approach without jumping.",
      "right_run_jump": "Already rising: sustain existing jump."
    }
  }
]
```

## 002-stage-3-4-r02

Reflected instructions retained in the immutable profile:
```json
[]
```

## 003-stage-3-4-r03

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 288,
    "max_x": 375,
    "instructions": "OVERRIDE: Is Mario grounded? Answer from the grounded field only.",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false: release jump."
    }
  }
]
```

## 004-stage-3-4-r04

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 288,
    "max_x": 375,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least12."
    }
  }
]
```

## 005-stage-3-4-r05

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 288,
    "max_x": 375,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least12."
    },
    "replace_instructions": true
  }
]
```

## 006-stage-3-4-r06

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 288,
    "max_x": 375,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least12."
    },
    "replace_instructions": true
  },
  {
    "id": "start-timing",
    "min_x": 0,
    "max_x": 42,
    "replace_instructions": true,
    "instructions": "Have at least 60 frames elapsed in start-timing?",
    "criteria": {
      "wait": "No, fewer than 60 frames elapsed.",
      "right_run_jump": "Yes, at least 60 frames elapsed."
    }
  }
]
```

## 007-stage-3-4-r07

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 288,
    "max_x": 375,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least12."
    },
    "replace_instructions": true
  },
  {
    "id": "lava-bubble-wait",
    "min_x": 370,
    "max_x": 407,
    "replace_instructions": true,
    "instructions": "Classify the number of elapsed frames in lava-bubble-wait.",
    "criteria": {
      "left": "Fewer than 16 frames elapsed.",
      "wait": "At least 16 but fewer than 60 frames elapsed.",
      "right_run_jump": "At least 60 frames elapsed."
    }
  }
]
```

## 008-stage-3-4-r08

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "short-hop-for-next-platform",
    "min_x": 288,
    "max_x": 375,
    "instructions": "OVERRIDE: Is Mario grounded OR jump_elapsed_frames less than12?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true or jump_elapsed_frames is less than12.",
      "right_run": "No, grounded is false and jump_elapsed_frames is at least12."
    },
    "replace_instructions": true
  },
  {
    "id": "lava-bubble-wait",
    "min_x": 370,
    "max_x": 407,
    "replace_instructions": true,
    "instructions": "Classify the number of elapsed frames in lava-bubble-wait.",
    "criteria": {
      "left": "Fewer than 16 frames elapsed.",
      "wait": "At least 16 but fewer than 60 frames elapsed.",
      "right_run_jump": "At least 60 frames elapsed."
    }
  },
  {
    "id": "second-bubble-wait",
    "min_x": 1485,
    "max_x": 1540,
    "replace_instructions": true,
    "instructions": "Classify the number of elapsed frames in second-bubble-wait.",
    "criteria": {
      "left": "Fewer than 16 frames elapsed.",
      "wait": "At least 16 but fewer than 60 frames elapsed.",
      "right_run_jump": "At least 60 frames elapsed."
    }
  }
]
```


## Verified result

First lava bubble required 16 frames braking followed by wait until60, then jump. Second bubble used wait until32; waiting60 collided with Bowser fire. A medium12 hop at1580 landed on middle lava bank. At the final ceiling/Bowser, running through2118 led to jump at2125 and success. Jump at2109 bonked the ceiling; jump at2136 hit Bowser before gaining height. Exact replay passed. Winner and runtime metadata uploaded AMD. See `deliverables/stages/3-4/result.json` and `first-win.mp4`.


## Final attempt ledger

| Attempt/profile | Maximum x | Completed | Stop reason |
|---|---:|---|---|
| 001-stage-3-4-r01 | 248 | False | terminated |
| 002-stage-3-4-r02 | 417 | False | terminated |
| 003-stage-3-4-r03 | 354 | False | terminated |
| 004-stage-3-4-r04 | 411 | False | terminated |
| 005-stage-3-4-r05 | 411 | False | terminated |
| 006-stage-3-4-r06 | 408 | False | terminated |
| 007-stage-3-4-r07 | 1544 | False | terminated |
| 008-stage-3-4-r08 | 1525 | False | terminated |
| 009-stage-3-4-r09 | 1765 | False | terminated |
| 010-stage-3-4-r10 | 2152 | False | terminated |
| 011-stage-3-4-r11 | 2156 | False | terminated |
| 012-stage-3-4-r12 | 2156 | False | terminated |
| 013-stage-3-4-r13 | 2168 | False | terminated |
| 014-stage-3-4-r14 | 2245 | True | completed |
| 015-stage-3-4-r15 | 2153 | False | terminated |
