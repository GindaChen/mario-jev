# World 6-3: final attempt ledger

44 reserved attempts against a budget of 100. 1 infrastructure error; 37 gameplay failure; 4 API error after gameplay; 2 clear.

Counts include infrastructure errors and cancelled trials. A clear requires a fresh completed summary; replay verification is recorded separately with the winner. Diagnostic scripted replay branches are excluded from this ledger. A terminal gameplay failure is still a completed experiment, not a completed level.

| Attempt | Profile snapshot | Manifest status | Observed outcome | Logged decisions | Max x |
|---|---|---|---|---:|---:|
| 001 | stage-6-3-r01 | error | infrastructure error: before first decision | 0 | — |
| 002 | stage-6-3-r01 | finished | gameplay failure: terminated | 76 | 777 |
| 003 | stage-6-3-r02 | finished | gameplay failure: terminated | 76 | 777 |
| 004 | stage-6-3-r03 | finished | gameplay failure: terminated | 67 | 681 |
| 005 | stage-6-3-r04 | finished | gameplay failure: stalled | 665 | 635 |
| 006 | stage-6-3-r05 | finished | gameplay failure: stalled | 665 | 635 |
| 007 | stage-6-3-r06 | finished | gameplay failure: terminated | 145 | 645 |
| 008 | stage-6-3-r07 | finished | gameplay failure: terminated | 83 | 618 |
| 009 | stage-6-3-r08 | finished | gameplay failure: terminated | 132 | 1206 |
| 010 | stage-6-3-r09 | finished | gameplay failure: terminated | 133 | 1221 |
| 011 | stage-6-3-r10 | finished | gameplay failure: terminated | 197 | 1953 |
| 012 | stage-6-3-r11 | finished | gameplay failure: terminated | 197 | 1953 |
| 013 | stage-6-3-r12 | finished | gameplay failure: terminated | 200 | 1989 |
| 014 | stage-6-3-r13 | finished | gameplay failure: terminated | 199 | 1977 |
| 015 | stage-6-3-r14 | finished | gameplay failure: terminated | 183 | 1788 |
| 016 | stage-6-3-r15 | finished | gameplay failure: terminated | 183 | 1788 |
| 017 | stage-6-3-r16 | error | API error after gameplay: partial trace retained | 185 | 1800 |
| 018 | stage-6-3-r17 | error | API error after gameplay: partial trace retained | 186 | 1812 |
| 019 | stage-6-3-r16 | error | API error after gameplay: partial trace retained | 185 | 1800 |
| 020 | stage-6-3-r17 | error | API error after gameplay: partial trace retained | 186 | 1812 |
| 021 | stage-6-3-r18 | finished | gameplay failure: stalled | 791 | 1854 |
| 022 | stage-6-3-r19 | finished | gameplay failure: terminated | 294 | 1863 |
| 023 | stage-6-3-r18 | finished | gameplay failure: stalled | 791 | 1854 |
| 024 | stage-6-3-r19 | finished | gameplay failure: terminated | 294 | 1863 |
| 025 | stage-6-3-r20 | finished | gameplay failure: stalled | 791 | 1854 |
| 026 | stage-6-3-r21 | finished | gameplay failure: terminated | 221 | 2113 |
| 027 | stage-6-3-r20 | finished | gameplay failure: stalled | 791 | 1854 |
| 028 | stage-6-3-r21 | finished | gameplay failure: terminated | 221 | 2113 |
| 029 | stage-6-3-r22 | finished | gameplay failure: terminated | 257 | 2521 |
| 030 | stage-6-3-r23 | finished | gameplay failure: terminated | 257 | 2521 |
| 031 | stage-6-3-r22 | finished | gameplay failure: terminated | 257 | 2521 |
| 032 | stage-6-3-r23 | finished | gameplay failure: terminated | 257 | 2521 |
| 033 | stage-6-3-r24 | finished | gameplay failure: terminated | 239 | 2311 |
| 034 | stage-6-3-r25 | finished | gameplay failure: terminated | 239 | 2311 |
| 035 | stage-6-3-r24 | finished | gameplay failure: terminated | 239 | 2311 |
| 036 | stage-6-3-r25 | finished | gameplay failure: terminated | 239 | 2311 |
| 037 | stage-6-3-r26 | finished | gameplay failure: terminated | 258 | 2473 |
| 038 | stage-6-3-r27 | finished | gameplay failure: terminated | 258 | 2473 |
| 039 | stage-6-3-r26 | finished | gameplay failure: terminated | 258 | 2473 |
| 040 | stage-6-3-r27 | finished | gameplay failure: terminated | 258 | 2473 |
| 041 | stage-6-3-r28 | finished | gameplay failure: terminated | 257 | 2518 |
| 042 | stage-6-3-r29 | finished | clear: completed | 270 | 2665 |
| 043 | stage-6-3-r28 | finished | gameplay failure: terminated | 257 | 2518 |
| 044 | stage-6-3-r29 | finished | clear: completed | 270 | 2665 |

Source: `runs/stages/6-3/batches/manifest.json` and immutable attempt traces. Each attempt directory retains its prompt snapshot, source snapshot, stdout, and available request/response trace.
