#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_NAME="home-pi-dashboard.service"
UPDATE_SERVICE_NAME="home-pi-dashboard-update.service"
UPDATE_TIMER_NAME="home-pi-dashboard-update.timer"
APP_SERVICE_PATH="$SYSTEMD_USER_DIR/$SERVICE_NAME"
UPDATE_SERVICE_PATH="$SYSTEMD_USER_DIR/$UPDATE_SERVICE_NAME"
UPDATE_TIMER_PATH="$SYSTEMD_USER_DIR/$UPDATE_TIMER_NAME"

mkdir -p "$SYSTEMD_USER_DIR"
chmod +x "$ROOT_DIR/scripts/run_on_pi3.sh" "$ROOT_DIR/scripts/update_and_restart_on_pi.sh"

cat >"$APP_SERVICE_PATH" <<EOF
[Unit]
Description=Home Pi Dashboard
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$ROOT_DIR
Environment=DISPLAY=:0
Environment=XAUTHORITY=%h/.Xauthority
Environment=QSG_RENDER_LOOP=basic
ExecStart=$ROOT_DIR/scripts/run_on_pi3.sh
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF

cat >"$UPDATE_SERVICE_PATH" <<EOF
[Unit]
Description=Update Home Pi Dashboard from main and restart if needed
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=$ROOT_DIR
Environment=DISPLAY=:0
Environment=XAUTHORITY=%h/.Xauthority
Environment=HOME_PI_DASHBOARD_SERVICE_NAME=$SERVICE_NAME
ExecStart=$ROOT_DIR/scripts/update_and_restart_on_pi.sh main
EOF

cat >"$UPDATE_TIMER_PATH" <<EOF
[Unit]
Description=Periodic update check for Home Pi Dashboard

[Timer]
OnBootSec=2min
OnUnitActiveSec=10min
Persistent=true
Unit=$UPDATE_SERVICE_NAME

[Install]
WantedBy=timers.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now "$SERVICE_NAME"
systemctl --user enable --now "$UPDATE_TIMER_NAME"

echo
echo "Installed user systemd units:"
echo "  $APP_SERVICE_PATH"
echo "  $UPDATE_SERVICE_PATH"
echo "  $UPDATE_TIMER_PATH"
echo
echo "Dashboard service status:"
systemctl --user --no-pager --full status "$SERVICE_NAME" || true
echo
echo "Update timer status:"
systemctl --user --no-pager --full status "$UPDATE_TIMER_NAME" || true
echo
echo "Useful commands:"
echo "  systemctl --user status $SERVICE_NAME"
echo "  systemctl --user restart $SERVICE_NAME"
echo "  systemctl --user status $UPDATE_TIMER_NAME"
echo "  journalctl --user -u $SERVICE_NAME -f"
