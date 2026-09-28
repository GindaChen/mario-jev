# World 5-3: final attempt ledger

23 reserved attempts against a budget of 100. 1 infrastructure error; 20 gameplay failure; 2 clear.

Counts include infrastructure errors and cancelled trials. A clear requires a fresh completed summary; replay verification is recorded separately with the winner. Diagnostic scripted replay branches are excluded from this ledger. A terminal gameplay failure is still a completed experiment, not a completed level.

| Attempt | Profile snapshot | Manifest status | Observed outcome | Logged decisions | Max x |
|---|---|---|---|---:|---:|
| 001 | stage-5-3-r01 | error | infrastructure error: before first decision | 0 | — |
| 002 | stage-5-3-r01 | finished | gameplay failure: terminated | 41 | 434 |
| 003 | stage-5-3-r02 | finished | gameplay failure: terminated | 16 | 183 |
| 004 | stage-5-3-r03 | finished | gameplay failure: terminated | 31 | 314 |
| 005 | stage-5-3-r04 | finished | gameplay failure: terminated | 40 | 422 |
| 006 | stage-5-3-r05 | finished | gameplay failure: terminated | 69 | 761 |
| 007 | stage-5-3-r06 | finished | gameplay failure: terminated | 70 | 738 |
| 008 | stage-5-3-r07 | finished | gameplay failure: terminated | 91 | 880 |
| 009 | stage-5-3-r08 | finished | gameplay failure: terminated | 90 | 937 |
| 010 | stage-5-3-r09 | finished | gameplay failure: terminated | 148 | 1563 |
| 011 | stage-5-3-r10 | finished | gameplay failure: terminated | 90 | 882 |
| 012 | stage-5-3-r10 | finished | gameplay failure: terminated | 152 | 1611 |
| 013 | stage-5-3-r10 | finished | gameplay failure: terminated | 152 | 1611 |
| 014 | stage-5-3-r11 | finished | gameplay failure: terminated | 142 | 1486 |
| 015 | stage-5-3-r12 | finished | gameplay failure: terminated | 142 | 1486 |
| 016 | stage-5-3-r13 | finished | gameplay failure: terminated | 90 | 882 |
| 017 | stage-5-3-r14 | finished | gameplay failure: terminated | 142 | 1465 |
| 018 | stage-5-3-r13 | finished | gameplay failure: terminated | 90 | 882 |
| 019 | stage-5-3-r14 | finished | gameplay failure: terminated | 90 | 882 |
| 020 | stage-5-3-r15 | finished | gameplay failure: terminated | 168 | 1457 |
| 021 | stage-5-3-r16 | finished | clear: completed | 285 | 2425 |
| 022 | stage-5-3-r15 | finished | gameplay failure: terminated | 168 | 1457 |
| 023 | stage-5-3-r16 | finished | clear: completed | 285 | 2425 |

Source: `runs/stages/5-3/batches/manifest.json` and immutable attempt traces. Each attempt directory retains its prompt snapshot, source snapshot, stdout, and available request/response trace.
