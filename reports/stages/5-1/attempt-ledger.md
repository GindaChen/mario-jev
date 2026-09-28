# World 5-1: final attempt ledger

8 reserved attempts against a budget of 100. 1 infrastructure error; 6 gameplay failure; 1 clear.

Counts include infrastructure errors and cancelled trials. A clear requires a fresh completed summary; replay verification is recorded separately with the winner. Diagnostic scripted replay branches are excluded from this ledger. A terminal gameplay failure is still a completed experiment, not a completed level.

| Attempt | Profile snapshot | Manifest status | Observed outcome | Logged decisions | Max x |
|---|---|---|---|---:|---:|
| 001 | stage-5-1-r01 | error | infrastructure error: before first decision | 0 | — |
| 002 | stage-5-1-r01 | finished | gameplay failure: terminated | 150 | 1731 |
| 003 | stage-5-1-r02 | finished | gameplay failure: terminated | 141 | 1621 |
| 004 | stage-5-1-r03 | finished | gameplay failure: terminated | 181 | 1972 |
| 005 | stage-5-1-r04 | finished | gameplay failure: terminated | 181 | 1972 |
| 006 | stage-5-1-r05 | finished | gameplay failure: terminated | 166 | 1845 |
| 007 | stage-5-1-r06 | finished | gameplay failure: terminated | 182 | 1972 |
| 008 | stage-5-1-r07 | finished | clear: completed | 338 | 3177 |

Source: `runs/stages/5-1/batches/manifest.json` and immutable attempt traces. Each attempt directory retains its prompt snapshot, source snapshot, stdout, and available request/response trace.
