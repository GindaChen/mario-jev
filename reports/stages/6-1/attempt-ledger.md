# World 6-1: final attempt ledger

4 reserved attempts against a budget of 100. 1 infrastructure error; 2 gameplay failure; 1 clear.

Counts include infrastructure errors and cancelled trials. A clear requires a fresh completed summary; replay verification is recorded separately with the winner. Diagnostic scripted replay branches are excluded from this ledger. A terminal gameplay failure is still a completed experiment, not a completed level.

| Attempt | Profile snapshot | Manifest status | Observed outcome | Logged decisions | Max x |
|---|---|---|---|---:|---:|
| 001 | stage-6-1-r01 | error | infrastructure error: before first decision | 0 | — |
| 002 | stage-6-1-r01 | finished | gameplay failure: terminated | 44 | 513 |
| 003 | stage-6-1-r02 | finished | gameplay failure: terminated | 108 | 1216 |
| 004 | stage-6-1-r03 | finished | clear: completed | 281 | 2969 |

Source: `runs/stages/6-1/batches/manifest.json` and immutable attempt traces. Each attempt directory retains its prompt snapshot, source snapshot, stdout, and available request/response trace.
