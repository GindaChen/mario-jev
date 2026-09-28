# World 5-2: final attempt ledger

8 reserved attempts against a budget of 100. 1 infrastructure error; 6 gameplay failure; 1 clear.

Counts include infrastructure errors and cancelled trials. A clear requires a fresh completed summary; replay verification is recorded separately with the winner. Diagnostic scripted replay branches are excluded from this ledger. A terminal gameplay failure is still a completed experiment, not a completed level.

| Attempt | Profile snapshot | Manifest status | Observed outcome | Logged decisions | Max x |
|---|---|---|---|---:|---:|
| 001 | stage-5-2-r01 | error | infrastructure error: before first decision | 0 | — |
| 002 | stage-5-2-r01 | finished | gameplay failure: terminated | 121 | 996 |
| 003 | stage-5-2-r02 | finished | gameplay failure: terminated | 136 | 1081 |
| 004 | stage-5-2-r03 | finished | gameplay failure: terminated | 188 | 1682 |
| 005 | stage-5-2-r04 | finished | gameplay failure: terminated | 259 | 2441 |
| 006 | stage-5-2-r05 | finished | gameplay failure: terminated | 308 | 2945 |
| 007 | stage-5-2-r06 | finished | gameplay failure: stalled | 906 | 2914 |
| 008 | stage-5-2-r07 | finished | clear: completed | 343 | 3193 |

Source: `runs/stages/5-2/batches/manifest.json` and immutable attempt traces. Each attempt directory retains its prompt snapshot, source snapshot, stdout, and available request/response trace.
