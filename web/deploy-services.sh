#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$HOME/.config/systemd/user"
cat > "$HOME/.config/systemd/user/game-lab-web.service" <<'UNIT'
[Unit]
Description=Game Lab public artifact website
After=network-online.target
[Service]
WorkingDirectory=/home/juc049/projects/game-lab
ExecStart=/usr/bin/python3 /home/juc049/projects/game-lab/server.py
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
[Install]
WantedBy=default.target
UNIT
cat > "$HOME/.config/systemd/user/game-lab-publisher.service" <<'UNIT'
[Unit]
Description=Game Lab read-only Mario experiment publisher
After=network-online.target
[Service]
WorkingDirectory=/home/juc049/projects/game-lab
ExecStart=/usr/bin/python3 /home/juc049/projects/game-lab/publisher.py
Environment=MARIO_HARNESS=/home/juc049/projects/mario-amd/harness
Environment=PYTHONUNBUFFERED=1
Environment=PATH=/home/juc049/projects/game-lab/bin:/usr/local/bin:/usr/bin:/bin
Restart=on-failure
RestartSec=5
Nice=10
CPUQuota=100%
NoNewPrivileges=true
[Install]
WantedBy=default.target
UNIT
cat > "$HOME/.cloudflared/game-lab.yml" <<'CONFIG'
tunnel: bad4a71d-4a00-4615-a76e-3abcbd127f9a
credentials-file: /home/juc049/.cloudflared/bad4a71d-4a00-4615-a76e-3abcbd127f9a.json
ingress:
  - hostname: game.gindachen.com
    service: http://127.0.0.1:18480
  - service: http_status:404
CONFIG
chmod 600 "$HOME/.cloudflared/game-lab.yml"
cat > "$HOME/.config/systemd/user/game-lab-tunnel.service" <<'UNIT'
[Unit]
Description=Cloudflare tunnel for game.gindachen.com
After=network-online.target game-lab-web.service
[Service]
ExecStart=/home/juc049/.local/bin/cloudflared tunnel --config /home/juc049/.cloudflared/game-lab.yml run
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
[Install]
WantedBy=default.target
UNIT
systemctl --user daemon-reload
systemctl --user enable --now game-lab-web.service game-lab-publisher.service game-lab-tunnel.service
