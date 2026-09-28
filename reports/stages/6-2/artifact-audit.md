# Worlds 5–6 artifact audit

Audit performed after all eight independent stages had verified winners. Each row passed checks for a fresh completed summary, replay verification, matching trace/profile SHA-256 values, identical frozen winner copies, matching runtime metadata, and a nonempty exported video. AMD winner hashes match the local copies; every AMD winner has runtime metadata.

| Stage | Winner | First winning attempt | Decisions | Max x | Endpoint port |
|---|---|---:|---:|---:|---:|
| 5-1 | r07 | 008 | 338 | 3177 | 18517 |
| 5-2 | r07 | 008 | 343 | 3193 | 18517 |
| 5-3 | r16 | 021 | 285 | 2425 | 18517 |
| 5-4 | r21 | 027 | 242 | 2259 | 18517 |
| 6-1 | r03 | 004 | 281 | 2969 | 18517 |
| 6-2 | r27 | 043 | 518 | 3449 | 18517 |
| 6-3 | r29 | 042 | 270 | 2665 | 18517 |
| 6-4 | r33 | 040 | 243 | 2259 | 18515 |

All winner runtimes use four-frame action intervals, seed 123, and history length 12. The existing grounded A-release mechanic may use a shorter interval where selected by the profile.

The eight final ledgers contain 204 reserved attempts: 8 infrastructure errors before the first decision, 177 completed experiments ending in gameplay failure, 14 fresh clear traces, 4 API errors after partial gameplay, and 1 partial run cancelled after the first 6-2 clear was verified. The extra clear traces come from already scheduled candidate repeats. These adaptively selected trials do not form an unbiased success-rate estimate.

Diagnostic scripted replay branches are separate development evidence and are not counted as stage attempts or clears. No active world 5/6 batch processes remained at the final process check. This audit establishes eight independent stage clears, not a continuous campaign.
