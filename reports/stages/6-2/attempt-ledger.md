# World 6-2: final attempt ledger

46 reserved attempts against a budget of 100. 1 infrastructure error; 42 gameplay failure; 2 clear; 1 cancelled partial run.

Counts include infrastructure errors and cancelled trials. A clear requires a fresh completed summary; replay verification is recorded separately with the winner. Diagnostic scripted replay branches are excluded from this ledger. A terminal gameplay failure is still a completed experiment, not a completed level.

| Attempt | Profile snapshot | Manifest status | Observed outcome | Logged decisions | Max x |
|---|---|---|---|---:|---:|
| 001 | stage-6-2-r01 | error | infrastructure error: before first decision | 0 | — |
| 002 | stage-6-2-r01 | finished | gameplay failure: terminated | 26 | 303 |
| 003 | stage-6-2-r02 | finished | gameplay failure: terminated | 130 | 815 |
| 004 | stage-6-2-r03 | finished | gameplay failure: terminated | 46 | 456 |
| 005 | stage-6-2-r04 | finished | gameplay failure: terminated | 94 | 520 |
| 006 | stage-6-2-r05 | finished | gameplay failure: terminated | 46 | 456 |
| 007 | stage-6-2-r06 | finished | gameplay failure: stalled | 729 | 885 |
| 008 | stage-6-2-r07 | finished | gameplay failure: terminated | 125 | 820 |
| 009 | stage-6-2-r08 | finished | gameplay failure: terminated | 26 | 307 |
| 010 | stage-6-2-r09 | finished | gameplay failure: terminated | 100 | 446 |
| 011 | stage-6-2-r10 | finished | gameplay failure: terminated | 82 | 415 |
| 012 | stage-6-2-r10 | finished | gameplay failure: terminated | 131 | 898 |
| 013 | stage-6-2-r11 | finished | gameplay failure: terminated | 82 | 416 |
| 014 | stage-6-2-r12 | finished | gameplay failure: terminated | 49 | 456 |
| 015 | stage-6-2-r13 | finished | gameplay failure: terminated | 214 | 1348 |
| 016 | stage-6-2-r13 | finished | gameplay failure: terminated | 214 | 1348 |
| 017 | stage-6-2-r14 | finished | gameplay failure: terminated | 222 | 1349 |
| 018 | stage-6-2-r15 | finished | gameplay failure: terminated | 222 | 1353 |
| 019 | stage-6-2-r16 | finished | gameplay failure: terminated | 255 | 1408 |
| 020 | stage-6-2-r14 | finished | gameplay failure: terminated | 222 | 1352 |
| 021 | stage-6-2-r15 | finished | gameplay failure: terminated | 82 | 416 |
| 022 | stage-6-2-r16 | finished | gameplay failure: terminated | 255 | 1408 |
| 023 | stage-6-2-r17 | finished | gameplay failure: terminated | 356 | 2178 |
| 024 | stage-6-2-r18 | finished | gameplay failure: terminated | 259 | 1392 |
| 025 | stage-6-2-r17 | finished | gameplay failure: terminated | 356 | 2178 |
| 026 | stage-6-2-r18 | finished | gameplay failure: terminated | 259 | 1392 |
| 027 | stage-6-2-r19 | finished | gameplay failure: terminated | 375 | 2451 |
| 028 | stage-6-2-r20 | finished | gameplay failure: stalled | 849 | 1379 |
| 029 | stage-6-2-r19 | finished | gameplay failure: terminated | 375 | 2451 |
| 030 | stage-6-2-r20 | finished | gameplay failure: terminated | 411 | 2684 |
| 031 | stage-6-2-r21 | finished | gameplay failure: terminated | 376 | 2463 |
| 032 | stage-6-2-r22 | finished | gameplay failure: terminated | 406 | 2685 |
| 033 | stage-6-2-r21 | finished | gameplay failure: terminated | 376 | 2463 |
| 034 | stage-6-2-r22 | finished | gameplay failure: terminated | 406 | 2685 |
| 035 | stage-6-2-r23 | finished | gameplay failure: stalled | 849 | 1379 |
| 036 | stage-6-2-r24 | finished | gameplay failure: terminated | 447 | 2862 |
| 037 | stage-6-2-r23 | finished | gameplay failure: terminated | 440 | 2868 |
| 038 | stage-6-2-r24 | finished | gameplay failure: terminated | 447 | 2862 |
| 039 | stage-6-2-r25 | finished | gameplay failure: terminated | 434 | 2784 |
| 040 | stage-6-2-r26 | finished | gameplay failure: terminated | 434 | 2784 |
| 041 | stage-6-2-r25 | finished | gameplay failure: terminated | 434 | 2784 |
| 042 | stage-6-2-r26 | finished | gameplay failure: stalled | 849 | 1379 |
| 043 | stage-6-2-r27 | finished | clear: completed | 518 | 3449 |
| 044 | stage-6-2-r28 | finished | gameplay failure: stalled | 849 | 1379 |
| 045 | stage-6-2-r27 | finished | clear: completed | 518 | 3449 |
| 046 | stage-6-2-r28 | error | cancelled partial run: stopped after first clear | 468 | 2870 |

Source: `runs/stages/6-2/batches/manifest.json` and immutable attempt traces. Each attempt directory retains its prompt snapshot, source snapshot, stdout, and available request/response trace.
