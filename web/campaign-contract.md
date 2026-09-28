# Live campaign website contract

Runner owns `/home/juc049/projects/mario-amd/harness/runs/overnight-campaign/status.json` and `latest-frame.jpg`, replacing them atomically. This website's `campaign_publisher.py` reads only those two fixed paths every2seconds and projects allowed fields into `/public/data/campaign.json` and `campaign-frame.jpg`. It does not run gameplay, infer completion from images, or expose runner configs, arbitrary files, endpoints, or mutation APIs.

Status fields: campaign_id, status, mode, started_at, updated_at, current_stage, current_attempt, cleared_stages, stage_results, restarts, total_decisions, counts, current, event_log. Timestamps are timezone-aware ISO8601 strings. `current.room` should be a scalar area-data address/string. `stage_results` is keyed by1-1 through8-4 with status/attempts/retries/checkpoint_retries/completed_at. Events have at/kind/stage/attempt/message. Counts are recomputed for recorded cleared stages; restart/decision totals come from the runner. Unknown private fields are dropped. Published JSON is sanitized, not the original status file.

Modes:
- continuous: runner preserves full-game state between stages.
- stage_linked: a separate stage environment was loaded. The page explicitly stops presenting this as a continuous game.
- continuous_with_recorded_restarts: supported alternate mode, explicitly says this is not uninterrupted.

The UI refreshes every2seconds and marks telemetry delayed after30seconds of runner inactivity or15seconds of publisher inactivity. Historical stage research remains separate at `/mario/`; previous wins never contribute to this campaign's stage count. There is no claimed wall-clock speedrun time. Frames are sampled emulator snapshots and simulation pauses during inference.

Deployment source is AMD `/home/juc049/projects/game-lab`; local working copy for this change is `game-lab-campaign`. Only new campaign assets/publisher/service and homepage navigation are deployed. Existing experiment publisher, replay service, web server and Cloudflare tunnel are unchanged.

## Deployment verified 2026-09-28

The dedicated `game-lab-campaign.service` is enabled and active on AMD. Existing
`game-lab-web`, research publisher, replay service, and Cloudflare tunnel were not
restarted. The previous homepage is retained in `backups/campaign-20260928/`.

Verification: four publisher unit tests passed both locally and on AMD; JS syntax
check passed. Public route redirects to its trailing slash, dashboard and JPEG
return HTTP 200, live data/images use no-store. Chrome showed fresh real gameplay,
changing request latency, attempts and restart counts; stage selection and journal
filters passed, with no console errors. It observed the first campaign clear and
transition into 1-2 (1/32 cleared, four recorded restarts). Screenshot is saved as
`dashboard-live.png` in the local website checkout. Independent `/mario/` remains
HTTP 200. The journal preserves initial infrastructure errors as well as deaths.

Public static JS uses a version query to avoid stale CDN/browser bundles. Progress
polls every two seconds; publisher does no inference or emulator work.

## Final replay and verification publication

No automatic video copy occurs. After actual completion and exact replay validation,
the campaign owner explicitly publishes final files to this directory on AMD:

`/home/juc049/projects/game-lab/public/data/campaign-final/<safe-campaign-slug>/`

Use a new slug containing only letters, digits, underscores and hyphens per campaign.
Publish the completed `campaign-replay.mp4` and a sanitized `verification.json`
(using temporary files then atomic rename). The verification file must include:

```json
{"campaign_id":"EXACT status.json campaign_id", "replay_verified":true, "completed":true}
```

Include useful public replay evidence in that same JSON (decisions checked, reset
counts, final outcome, video checksum); exclude private filesystem paths/API settings.
If the internal verifier has another schema, create this public summary only from its
successful final result. Never set these booleans to bypass an incomplete audit.

Then atomically update the source status.json (preserving its other fields):

```json
{"artifacts": {
  "replay_url":"/data/campaign-final/<safe-campaign-slug>/campaign-replay.mp4",
  "verification_url":"/data/campaign-final/<safe-campaign-slug>/verification.json"
}}
```

The publisher exposes both links only when status is `completed`, all 32 stage
clears are recorded, both nonempty published files exist in the same campaign
folder, and the public verification JSON matches the campaign ID with both
booleans true. Paths outside the fixed namespace, remote URLs, traversal and
symlinks escaping the campaign-final directory are rejected. The dashboard
shows the verified replay section only when this gate succeeds. No placeholder
links, partial replay export, or arbitrary status.artifacts values are published.
The existing HTTP server already supports video byte ranges.

### Final replay variants (updated contract)

The public verification wrapper must now explicitly identify the primary replay.
The earlier minimal three-field wrapper alone no longer enables links. Example:

```json
{
  "campaign_id": "EXACT status.json campaign_id",
  "completed": true,
  "replay_verified": true,
  "replays": {
    "full": {"file": "campaign-replay.mp4", "kind": "chronological_attempts", "verified": true},
    "clears": {"file": "campaign-clears.mp4", "kind": "stitched_stage_clears", "verified": true}
  },
  "audit_archive": {"file": "campaign-audit.tar.gz", "verified": true}
}
```

`replays.full` is required. `replays.clears` and `audit_archive` are optional; omit
unproduced artifacts. Each true value must come from actual verification. The full
video includes chronological attempts and failures; the optional clears video is
a stitched compilation of successful stage attempts with retries omitted. Neither
variant changes the campaign's recorded continuity mode.

Optional source status.artifacts keys are `clears_url` and `audit_url`, using the
same folder as replay_url and verification_url and exact filenames above. Each
optional link requires its matching audit entry plus an existing nonempty file.
The public UI labels these separately and never calls the compilation continuous.
Only copy the final audit archive after reviewing its contents for publishable
traces/metadata; omit API settings, credentials and private host paths.
