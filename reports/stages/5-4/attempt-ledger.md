# World 5-4: final attempt ledger

30 reserved attempts against a budget of 100. 1 infrastructure error; 25 gameplay failure; 4 clear.

Counts include infrastructure errors and cancelled trials. A clear requires a fresh completed summary; replay verification is recorded separately with the winner. Diagnostic scripted replay branches are excluded from this ledger. A terminal gameplay failure is still a completed experiment, not a completed level.

| Attempt | Profile snapshot | Manifest status | Observed outcome | Logged decisions | Max x |
|---|---|---|---|---:|---:|
| 001 | stage-5-4-r01 | error | infrastructure error: before first decision | 0 | — |
| 002 | stage-5-4-r01 | finished | gameplay failure: terminated | 23 | 248 |
| 003 | stage-5-4-r02 | finished | gameplay failure: terminated | 31 | 344 |
| 004 | stage-5-4-r03 | finished | gameplay failure: terminated | 29 | 320 |
| 005 | stage-5-4-r04 | finished | gameplay failure: terminated | 111 | 1118 |
| 006 | stage-5-4-r05 | finished | gameplay failure: terminated | 110 | 1115 |
| 007 | stage-5-4-r06 | finished | gameplay failure: terminated | 111 | 1118 |
| 008 | stage-5-4-r07 | finished | gameplay failure: terminated | 190 | 1744 |
| 009 | stage-5-4-r08 | finished | gameplay failure: stalled | 767 | 1714 |
| 010 | stage-5-4-r09 | finished | gameplay failure: terminated | 178 | 1735 |
| 011 | stage-5-4-r10 | finished | gameplay failure: terminated | 179 | 1734 |
| 012 | stage-5-4-r11 | finished | gameplay failure: terminated | 170 | 1745 |
| 013 | stage-5-4-r12 | finished | gameplay failure: terminated | 158 | 1604 |
| 014 | stage-5-4-r13 | finished | gameplay failure: terminated | 170 | 1745 |
| 015 | stage-5-4-r14 | finished | gameplay failure: terminated | 178 | 1736 |
| 016 | stage-5-4-r15 | finished | gameplay failure: terminated | 178 | 1736 |
| 017 | stage-5-4-r16 | finished | gameplay failure: terminated | 178 | 1749 |
| 018 | stage-5-4-r17 | finished | gameplay failure: terminated | 178 | 1746 |
| 019 | stage-5-4-r18 | finished | gameplay failure: terminated | 178 | 1746 |
| 020 | stage-5-4-r16 | finished | gameplay failure: terminated | 178 | 1749 |
| 021 | stage-5-4-r17 | finished | gameplay failure: terminated | 178 | 1746 |
| 022 | stage-5-4-r18 | finished | gameplay failure: terminated | 178 | 1746 |
| 023 | stage-5-4-r19 | finished | gameplay failure: terminated | 190 | 1770 |
| 024 | stage-5-4-r20 | finished | gameplay failure: terminated | 221 | 2086 |
| 025 | stage-5-4-r19 | finished | gameplay failure: terminated | 190 | 1770 |
| 026 | stage-5-4-r20 | finished | gameplay failure: terminated | 221 | 2086 |
| 027 | stage-5-4-r21 | finished | clear: completed | 242 | 2259 |
| 028 | stage-5-4-r22 | finished | clear: completed | 242 | 2259 |
| 029 | stage-5-4-r21 | finished | clear: completed | 242 | 2259 |
| 030 | stage-5-4-r22 | finished | clear: completed | 242 | 2259 |

Source: `runs/stages/5-4/batches/manifest.json` and immutable attempt traces. Each attempt directory retains its prompt snapshot, source snapshot, stdout, and available request/response trace.
