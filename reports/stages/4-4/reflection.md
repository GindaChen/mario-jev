# Stage 4-4: offline reflection history

Each attempt is a fresh AMD simulation with DJev choosing every live action. GPT edits stored questions between attempts. Regional lessons are stage-specific coaching, not a zero-shot policy. Derived terrain uses explicitly enabled observed tile IDs where needed.

| Attempt | Profile | Max x | Completed | Stop |
|---|---|---:|---|---|
| 001-stage-4-4-r01 | 4-4-r01-hazards | 1031 | False | stalled |
| 002-stage-4-4-r02 | 4-4-r02-motion-jumps | 1055 | False | terminated |
| 003-stage-4-4-r03 | 4-4-r03-castle-perception | 1432 | False | terminated |
| 004-stage-4-4-r04 | 4-4-r04-rise-onto-lava-platform | 2087 | False | terminated |
| 005-stage-4-4-r05 | 4-4-r05-upper-route | 1842 | False | terminated |
| 006-stage-4-4-r06 | 4-4-r06-precise-takeoff | 2076 | False | terminated |

## 001-stage-4-4-r01

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

## 002-stage-4-4-r02

Reflected instructions retained in the immutable profile:
```json
[]
```

## 004-stage-4-4-r04

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "rise-early",
    "min_x": 1300,
    "max_x": 1520,
    "replace_instructions": true,
    "instructions": "Is Mario falling? Answer using the motion field only.",
    "criteria": {
      "right_run": "Yes, motion is falling.",
      "right_run_jump": "No, motion is grounded or rising or airborne."
    }
  }
]
```

## 005-stage-4-4-r05

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "rise-early",
    "min_x": 1300,
    "max_x": 1520,
    "replace_instructions": true,
    "instructions": "Is Mario falling? Answer using the motion field only.",
    "criteria": {
      "right_run": "Yes, motion is falling.",
      "right_run_jump": "No, motion is grounded or rising or airborne."
    }
  },
  {
    "id": "stay-upper-maze",
    "min_x": 1520,
    "max_x": 2150,
    "replace_instructions": true,
    "instructions": "Is Mario falling? Answer using the motion field only.",
    "criteria": {
      "right_run": "Yes, motion is falling.",
      "right_run_jump": "No, motion is grounded or rising or airborne."
    }
  }
]
```

## 006-stage-4-4-r06

Reflected instructions retained in the immutable profile:
```json
[
  {
    "id": "rise-early",
    "min_x": 1300,
    "max_x": 1520,
    "replace_instructions": true,
    "instructions": "Is Mario falling? Answer using the motion field only.",
    "criteria": {
      "right_run": "Yes, motion is falling.",
      "right_run_jump": "No, motion is grounded or rising or airborne."
    }
  },
  {
    "id": "first-upper-gap",
    "min_x": 1520,
    "max_x": 1600,
    "replace_instructions": true,
    "instructions": "Is x less than 1552?",
    "criteria": {
      "right_run": "Yes, x is less than 1552.",
      "right_run_jump": "No, x is at least 1552."
    }
  },
  {
    "id": "second-upper-gap",
    "min_x": 1690,
    "max_x": 1765,
    "replace_instructions": true,
    "instructions": "Is x less than 1716?",
    "criteria": {
      "right_run": "Yes, x is less than 1716.",
      "right_run_jump": "No, x is at least 1716."
    }
  }
]
```

Maze correction: primary disassembly requires grounded feet208 at secondgate. Online walkthrough clarified entering bottom by first dropping fromupper to middle, then walking LEFT through narrow entrance. Source: https://gamefaqs.gamespot.com/nes/525243-super-mario-bros/faqs/66598 . Offline forward-descent probes failed and are diagnostic only. r09 asks DJev to retreat left until feet>=192 then returnright; no forced liveaction overrides.


## Verified result

First clear: attempt 13, r13; attempt 14 r14 also cleared. Exact replay of attempt 13 passed. Both use normal castle maze checkpoints, no warp or state changes. Final bridge fix: medium 12-frame jump2530–2650, then at2580 brake left16frames, wait until24frames, resume jump. Compared with r11 (wait32), the shorter wait preserves enough speed to pass Bowser before descending. r14 adds 8 frames run before jumping and also passes. Winner/runtime uploaded AMD; video deliverables/stages/4-4/first-win.mp4.


## Final attempt ledger

| Attempt/profile | Maximum x | Completed | Stop reason |
|---|---:|---|---|
| 001-stage-4-4-r01 | 1031 | False | stalled |
| 002-stage-4-4-r02 | 1055 | False | terminated |
| 003-stage-4-4-r03 | 1432 | False | terminated |
| 004-stage-4-4-r04 | 2087 | False | terminated |
| 005-stage-4-4-r05 | 1842 | False | terminated |
| 006-stage-4-4-r06 | 2076 | False | terminated |
| 007-stage-4-4-r07 | 2102 | False | terminated |
| 008-stage-4-4-r08 | 2073 | False | terminated |
| 009-stage-4-4-r09 | 2568 | False | terminated |
| 010-stage-4-4-r10 | 2631 | False | terminated |
| 011-stage-4-4-r11 | 2685 | False | terminated |
| 012-stage-4-4-r12 | 2657 | False | terminated |
| 013-stage-4-4-r13 | 2772 | True | completed |
| 014-stage-4-4-r14 | 2770 | True | completed |
