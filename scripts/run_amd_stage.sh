#!/usr/bin/env bash
# Fresh independent stage run using a verified stage-specific DJev profile.
set -euo pipefail
cd "$(dirname "$0")/.."
world="${1:-1}"
stage="${2:-3}"
if (( $# >= 2 )); then shift 2; elif (( $# == 1 )); then shift; fi
profile="prompts/stages/${world}-${stage}/winner.json"
if [[ ! -f "$profile" ]]; then
  echo "No verified profile for ${world}-${stage}: $profile" >&2
  exit 2
fi
read -r frames decisions stall seed history endpoint < <(
  .venv/bin/python - "prompts/stages/${world}-${stage}/winner-runtime.json" <<'PYRUNTIME'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text()) if p.exists() else {}
print(d.get("frames", 4), d.get("decisions", 2000),
      d.get("stall_decisions", 600), d.get("seed", 123), d.get("history", 12),
      d.get("djev_url", "http://127.0.0.1:18515"))
PYRUNTIME
)
exec .venv/bin/mario-jev --policy djev \
  --djev-url "$endpoint" --djev-api-path /v1/systemone \
  --djev-profile "$profile" --world "$world" --stage "$stage" --headless \
  --frames "$frames" --decisions "$decisions" --stall-decisions "$stall" \
  --seed "$seed" --history "$history" --log-dir "runs/stage-play/${world}-${stage}" "$@"
