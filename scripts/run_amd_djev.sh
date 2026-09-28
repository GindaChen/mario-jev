#!/usr/bin/env bash
# Run on amd; simulator and the GPU7 DJev service communicate over loopback.
set -euo pipefail
cd "$(dirname "$0")/.."
exec .venv/bin/mario-jev --policy djev \
  --djev-url http://127.0.0.1:18515 --djev-api-path /v1/systemone \
  --djev-profile prompts/reflection/r35.json --world 1 --stage 2 --headless \
  --decisions 2000 --log-dir runs/djev-reflection-play "$@"
