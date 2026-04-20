#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BRANCH="${1:-main}"
LOG_DIR="$ROOT_DIR/.runtime"
LOG_FILE="$LOG_DIR/dashboard.log"
APP_PATTERN="home-pi-dashboard|python -m homehub.main"

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

start_dashboard() {
  if [[ -z "${DISPLAY:-}" ]]; then
    export DISPLAY=:0
  fi

  echo "Starting dashboard ..."
  nohup "$ROOT_DIR/scripts/run_on_pi3.sh" >"$LOG_FILE" 2>&1 &
  echo "Dashboard started."
  echo "Log file: $LOG_FILE"
}

if [[ "$LOCAL_SHA" == "$REMOTE_SHA" ]]; then
  echo "Already up to date on $BRANCH ($LOCAL_SHA)."
  if is_dashboard_running; then
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

if is_dashboard_running; then
  echo "Stopping running dashboard ..."
  pkill -TERM -u "$USER" -f "$APP_PATTERN" || true
  sleep 2
  pkill -KILL -u "$USER" -f "$APP_PATTERN" || true
fi

echo "Restarting dashboard after update ..."
start_dashboard
