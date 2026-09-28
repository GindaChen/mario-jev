# Stage 4-2: offline reflection history

Each attempt is a fresh AMD simulation with DJev choosing every live action. GPT edits stored questions between attempts. Regional lessons are stage-specific coaching, not a zero-shot policy. Derived terrain uses explicitly enabled observed tile IDs where needed.

| Attempt | Profile | Max x | Completed | Stop |
|---|---|---:|---|---|
| 001-stage-4-2-r01 | 4-2-r01-hazards | 345 | False | terminated |
| 002-stage-4-2-r02 | 4-2-r02-motion-jumps | 335 | False | terminated |
| 003-stage-4-2-r03 | 4-2-r03-reflect-first-failure | 198 | False | terminated |
| 004-stage-4-2-r04 | 4-2-r04-reflection | 345 | False | terminated |
| 005-stage-4-2-r05 | 4-2-r05-standalone-notes | 2866 | False | terminated |
| 006-stage-4-2-r06 | 4-2-r06-upper-route | 2868 | False | terminated |
| 007-stage-4-2-r07 | 4-2-r07-precise-takeoff | 2866 | False | terminated |
| 008-stage-4-2-r08 | 4-2-r08-landing-reflection | 2866 | False | terminated |

## 001-stage-4-2-r01

Reflected instructions retained in the immutable profile:
```json
[]
```

## 003-stage-4-2-r03

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "approach-island",
    "min_x": 0,
    "max_x": 174,
    "instructions": "OVERRIDE: Is x less than175?",
    "criteria": {
      "right_run": "Yes, x is less than175.",
      "right_run_jump": "No, x is175orhigher."
    }
  },
  {
    "id": "short-first-hop",
    "min_x": 175,
    "max_x": 270,
    "instructions": "OVERRIDE: Is Mario grounded?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false: release jump."
    }
  }
]
```

## 004-stage-4-2-r04

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "approach-island",
    "min_x": 0,
    "max_x": 150,
    "instructions": "OVERRIDE: Is x less than151?",
    "criteria": {
      "right_run": "Yes, x is less than151.",
      "right_run_jump": "No, x is151orhigher."
    }
  },
  {
    "id": "short-first-hop",
    "min_x": 151,
    "max_x": 240,
    "instructions": "OVERRIDE: Is Mario grounded?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false."
    }
  }
]
```

## 005-stage-4-2-r05

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "approach-island",
    "min_x": 0,
    "max_x": 150,
    "instructions": "OVERRIDE: Is x less than151?",
    "criteria": {
      "right_run": "Yes, x is less than151.",
      "right_run_jump": "No, x is151orhigher."
    },
    "replace_instructions": true
  },
  {
    "id": "short-first-hop",
    "min_x": 151,
    "max_x": 225,
    "instructions": "OVERRIDE: Is Mario grounded?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false."
    },
    "replace_instructions": true
  }
]
```

## 006-stage-4-2-r06

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "approach-island",
    "min_x": 0,
    "max_x": 150,
    "instructions": "OVERRIDE: Is x less than151?",
    "criteria": {
      "right_run": "Yes, x is less than151.",
      "right_run_jump": "No, x is151orhigher."
    },
    "replace_instructions": true
  },
  {
    "id": "short-first-hop",
    "min_x": 151,
    "max_x": 225,
    "instructions": "OVERRIDE: Is Mario grounded?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false."
    },
    "replace_instructions": true
  },
  {
    "id": "land-on-pipe-step",
    "min_x": 2790,
    "max_x": 2910,
    "replace_instructions": true,
    "instructions": "Have at least 12 frames elapsed in land-on-pipe-step?",
    "criteria": {
      "left_jump": "No, fewer than 12 frames elapsed: brake left while holding jump.",
      "right_run_jump": "Yes, at least 12 frames elapsed: move right holding jump."
    }
  }
]
```

## 007-stage-4-2-r07

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "approach-island",
    "min_x": 0,
    "max_x": 150,
    "instructions": "OVERRIDE: Is x less than151?",
    "criteria": {
      "right_run": "Yes, x is less than151.",
      "right_run_jump": "No, x is151orhigher."
    },
    "replace_instructions": true
  },
  {
    "id": "short-first-hop",
    "min_x": 151,
    "max_x": 225,
    "instructions": "OVERRIDE: Is Mario grounded?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false."
    },
    "replace_instructions": true
  },
  {
    "id": "land-on-pipe-step",
    "min_x": 2790,
    "max_x": 2910,
    "replace_instructions": true,
    "instructions": "Have at least 20 frames elapsed in land-on-pipe-step?",
    "criteria": {
      "left_jump": "No, fewer than 20 frames elapsed: brake left while holding jump.",
      "right_run_jump": "Yes, at least 20 frames elapsed: move right holding jump."
    }
  }
]
```

## 008-stage-4-2-r08

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "approach-island",
    "min_x": 0,
    "max_x": 150,
    "instructions": "OVERRIDE: Is x less than151?",
    "criteria": {
      "right_run": "Yes, x is less than151.",
      "right_run_jump": "No, x is151orhigher."
    },
    "replace_instructions": true
  },
  {
    "id": "short-first-hop",
    "min_x": 151,
    "max_x": 225,
    "instructions": "OVERRIDE: Is Mario grounded?",
    "criteria": {
      "right_run_jump": "Yes, grounded is true.",
      "right_run": "No, grounded is false."
    },
    "replace_instructions": true
  },
  {
    "id": "land-on-pipe-step",
    "min_x": 2770,
    "max_x": 2910,
    "replace_instructions": true,
    "instructions": "Have at least 24 frames elapsed in land-on-pipe-step?",
    "criteria": {
      "left_jump": "No, fewer than 24 frames elapsed: brake left while holding jump.",
      "right_run_jump": "Yes, at least 24 frames elapsed: move right holding jump."
    }
  }
]
```


## Verified result

Verified first clear: attempt11 r11, exact replay passed. Release jump near2930 to walk into the normal horizontal exit pipe at feet160. Continued to flag via ordinary exit; no warp zone. Earlier narrow step2816 required braking in flight followed by a grounded run until2822 before takeoff, preserving horizontal speed. Winner and runtime uploaded AMD. Video deliverables/stages/4-2/first-win.mp4.


## Final attempt ledger

| Attempt/profile | Maximum x | Completed | Stop reason |
|---|---:|---|---|
| 001-stage-4-2-r01 | 345 | False | terminated |
| 002-stage-4-2-r02 | 335 | False | terminated |
| 003-stage-4-2-r03 | 198 | False | terminated |
| 004-stage-4-2-r04 | 345 | False | terminated |
| 005-stage-4-2-r05 | 2866 | False | terminated |
| 006-stage-4-2-r06 | 2868 | False | terminated |
| 007-stage-4-2-r07 | 2866 | False | terminated |
| 008-stage-4-2-r08 | 2866 | False | terminated |
| 009-stage-4-2-r09 | 2868 | False | terminated |
| 010-stage-4-2-r10 | 3010 | False | stalled |
| 011-stage-4-2-r11 | 3161 | True | completed |
