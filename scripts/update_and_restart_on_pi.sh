#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BRANCH="${1:-main}"
LOG_DIR="$ROOT_DIR/.runtime"
LOG_FILE="$LOG_DIR/dashboard.log"
APP_PATTERN="home-pi-dashboard|python -m homehub.main"
SYSTEMD_SERVICE_NAME="${HOME_PI_DASHBOARD_SERVICE_NAME:-home-pi-dashboard.service}"

mkdir -p "$LOG_DIR"

if ! command -v git >/dev/null 2>&1; then
  echo "git is required but was not found."
  exit 1
fi

if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo "Working tree has local tracked changes. Refusing to auto-pull over them."
  echo "Commit or stash your local changes first."
  exit 1
fi

echo "Fetching latest commits from origin/$BRANCH ..."
git fetch origin "$BRANCH"

LOCAL_SHA="$(git rev-parse HEAD)"
REMOTE_SHA="$(git rev-parse "origin/$BRANCH")"

is_dashboard_running() {
  pgrep -u "$USER" -f "$APP_PATTERN" >/dev/null 2>&1
}

has_user_systemd_service() {
  command -v systemctl >/dev/null 2>&1 \
    && systemctl --user list-unit-files "$SYSTEMD_SERVICE_NAME" 2>/dev/null | grep -q "^$SYSTEMD_SERVICE_NAME"
}

start_dashboard() {
  if has_user_systemd_service; then
    echo "Starting dashboard via systemd user service ..."
    systemctl --user start "$SYSTEMD_SERVICE_NAME"
    echo "Dashboard started via $SYSTEMD_SERVICE_NAME."
    return
  fi

  if [[ -z "${DISPLAY:-}" ]]; then
    export DISPLAY=:0
  fi

  echo "Starting dashboard ..."
  nohup "$ROOT_DIR/scripts/run_on_pi3.sh" >"$LOG_FILE" 2>&1 &
  echo "Dashboard started."
  echo "Log file: $LOG_FILE"
}

stop_dashboard() {
  if has_user_systemd_service; then
    echo "Stopping dashboard via systemd user service ..."
    systemctl --user stop "$SYSTEMD_SERVICE_NAME"
    return
  fi

  if is_dashboard_running; then
    echo "Stopping running dashboard ..."
    pkill -TERM -u "$USER" -f "$APP_PATTERN" || true
    sleep 2
    pkill -KILL -u "$USER" -f "$APP_PATTERN" || true
  fi
}

restart_dashboard() {
  if has_user_systemd_service; then
    echo "Restarting dashboard via systemd user service ..."
    systemctl --user restart "$SYSTEMD_SERVICE_NAME"
    echo "Dashboard restarted via $SYSTEMD_SERVICE_NAME."
    return
  fi

  stop_dashboard
  start_dashboard
}

if [[ "$LOCAL_SHA" == "$REMOTE_SHA" ]]; then
  echo "Already up to date on $BRANCH ($LOCAL_SHA)."
  if has_user_systemd_service; then
    if systemctl --user --quiet is-active "$SYSTEMD_SERVICE_NAME"; then
      echo "Dashboard is already running via $SYSTEMD_SERVICE_NAME."
      exit 0
    fi
  elif is_dashboard_running; then
    echo "Dashboard is already running."
    exit 0
  fi
  echo "Dashboard is not running."
  start_dashboard
  exit 0
fi

echo "Update found:"
echo "  local : $LOCAL_SHA"
echo "  remote: $REMOTE_SHA"
echo "Pulling latest code ..."
git pull --ff-only origin "$BRANCH"

echo "Restarting dashboard after update ..."
restart_dashboard
