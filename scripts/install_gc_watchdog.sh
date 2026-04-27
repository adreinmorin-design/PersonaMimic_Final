#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIT_DIR="${HOME}/.config/systemd/user"
SERVICE_NAME="personamimic-storage-guardian.service"
TIMER_NAME="personamimic-storage-guardian.timer"

mkdir -p "${UNIT_DIR}"

cat > "${UNIT_DIR}/${SERVICE_NAME}" <<EOF
[Unit]
Description=PersonaMimic storage guardian

[Service]
Type=oneshot
WorkingDirectory=${PROJECT_ROOT}
ExecStart=/usr/bin/env python3 ${PROJECT_ROOT}/scripts/gc_watchdog.py --once
EOF

cat > "${UNIT_DIR}/${TIMER_NAME}" <<EOF
[Unit]
Description=Run PersonaMimic storage guardian every 30 minutes

[Timer]
OnBootSec=5m
OnUnitActiveSec=30m
Persistent=true
Unit=${SERVICE_NAME}

[Install]
WantedBy=timers.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now "${TIMER_NAME}"
systemctl --user start "${SERVICE_NAME}"

echo "Installed ${SERVICE_NAME} and ${TIMER_NAME}"
systemctl --user --no-pager --full status "${TIMER_NAME}" || true
