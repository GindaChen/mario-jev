# Game Lab

Public site: https://game.gindachen.com/
Mario campaign: https://game.gindachen.com/mario/

## Deployment

Versioned source is `web/` in the Mario harness repository. The deployed copy remains a separate directory on AMD.
AMD installation: `/home/juc049/projects/game-lab`.
Cloudflare tunnel: `game-lab`, with hostname `game.gindachen.com` and origin `127.0.0.1:18480`.
Only the `public/` directory is served. There are no mutation endpoints, exposed inference APIs, or public workspace directories.

Dedicated user services:
- `game-lab-web`: Python artifact server, including byte-range replay requests.
- `game-lab-publisher`: indexes allowed Mario logs every 15 seconds. One CPU-only replay exporter creates first-clear videos; no model calls.
- `game-lab-tunnel`: separate Cloudflare connection. Existing tunnel configuration and experiment services are untouched.

```sh
ssh amd 'systemctl --user status game-lab-web game-lab-publisher game-lab-tunnel'
```

## Automatic updates

The publisher reads these paths under `/home/juc049/projects/mario-amd/harness`:
- `runs/stages/<world-stage>/<profile>/*.jsonl`
- `runs/stages/<world-stage>/batches/<attempt>/*.jsonl`
- `runs/stage-play/**/*.jsonl`
- `runs/djev-reflection-100/*/*.jsonl`
- The original DJev World1-1 clear, `runs/20260926T221401248810Z.jsonl`.

Only fresh DJev runs count. Resume runs and other model policies are excluded. Partial JSONL lines are ignored and retried. Unfinished logs inactive for 180 seconds display as incomplete, not running. Run timestamps, outcomes, action/latency fields, prompt identity, and stage memory are projected into public summaries; raw configuration, URLs, credentials, and chat transcripts are never published. Profile snapshots are used when available.

The browser polls every 15 seconds, so end-to-end display can lag up to roughly 30 seconds. It displays a stale-feed warning after 90 seconds. Winner replays export automatically on the next 45-second sweep; they are ordinary 60fps game replays, not live wall-clock video. Replay export uses the harness's existing deterministic replay script and a site-local ffmpeg binary from imageio-ffmpeg. The publisher is low priority and CPU-capped to one core. It does not touch the GPU.

Saved reflection reports from the Mac also sync: `sync_notes.py` reads only `mario-jev/reports/stages/*/reflection.md` and the completed World1-2 analysis. A LaunchAgent (`com.gindachen.game-lab-notes`) checks every 60 seconds and sends only the changed public journal JSON over SSH. Absolute local paths are redacted. Reports require this Mac to be awake and connected; AMD run updates continue independently. The browser refreshes journals every 60 seconds. Unsaved chat commentary is not part of the feed.

Future stages are discovered automatically when written into the supported paths. Additional games can add another route under `public/` and a homepage card.

## Result semantics

- First clear is a recorded successful run; it is not a reliability estimate.
- Validated1-2 refers to the closed20/20 frozen validation (r35/r36, fixed reset scenario).
- Validated1-3 refers to six frozen validations (r24/r25, three each), documented in the published reflection report. These two validation claims are explicitly curated; later stages require a new verified claim rather than inferring validation from win counts.
- Raw counts include discovery and ablations. Stage clears start independently, not in a continuous campaign.
- The model weights are unchanged; stage-specific prompting and controller changes are allowed. Inference pauses the emulator.

## Verify and update

```sh
python3 test_publisher.py
MARIO_HARNESS=/path/to/mario-jev python3 publisher.py --once
python3 server.py
```

Use rsync for source updates, exclude `.notes-published`, logs, screenshots, `public/data`, `vendor`, and `bin`. Do not use `--delete`: remotely generated data and videos must be preserved. Restart only the Game Lab service whose code changed. Static assets do not need a restart. Cloudflare tunnel creation and DNS already exist; do not recreate them.

The site-local `vendor/imageio_ffmpeg` supplies the Linux ffmpeg binary linked as `bin/ffmpeg`. Install without changing the experiment venv:
`python3 -m pip install --target vendor imageio-ffmpeg`.

Cloudflare configuration is outside the public tree. Never copy tunnel credentials, private keys, or the origin certificate into this directory.

## Version2: trial-by-trial research history

The Mario page plots every trial in start-time order with a best-so-far step line. Click a point or use the trial picker for result deltas, saved reflection excerpts, and exact field-level policy diffs. Prompt revision markers compare a canonical hash of published policy fields, excluding the profile name.

For stages with a recorded clear, progress is a retrospective spatial proxy `(furthest x - initial x)/(first-clear max x - initial x)`. Only an explicit completed summary receives100%; unsuccessful runs are capped at99.5%. Stages without a finish reference use raw x. This is not route-aware distance: warps, loops, transitions and falling can make x misleading.

Diffs compare adjacent chronological trials, not asserted parent-child ancestry. Source hashes show when controller code changed as well. Missing full profile snapshots are labeled partial. Saved report passages are matched by explicit revision identifier; they are retrospective published explanations, never invented rationales or private reasoning. If none matches, the view says so.

Publisher schema2 adds start_x, source_sha256, policy_sha256, finish_x, and allowlisted prompt_config to the generated run summaries. Existing result and journal publishing is unchanged.

## Campaign research page

`/mario-speedrun/` is a dedicated page linked prominently from the homepage. It embeds both verified replays, explains stage loading versus uninterrupted play, shows all 62 attempt chapters, and displays five evidence-based reflection stories with exact profile diffs. The original independent-stage experiment remains at `/mario/`.

Rebuild the frozen public record with `python3 build_campaign_research.py --campaign-root /path/to/runs/overnight-campaign`. This reads the immutable trajectory and profiles, validates outcome counts, source-profile hashes and replay frame totals, and produces `public/data/campaign-research.json` plus byte-identical prompt snapshots. It does not run gameplay or modify the recorded campaign. The frontend requires the research campaign ID to match the verified replay feed. Reflection prose is retrospective and excludes private reasoning; unused candidate prompts are labeled.

Deployment is static-file-only: sync the two index pages, campaign.js, campaign-research.js/css, and campaign-research data directory. The existing server and publisher do not need restarting.
