#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BRANCH="${1:-main}"
LOG_DIR="$ROOT_DIR/.runtime"
LOG_FILE="$LOG_DIR/dashboard.log"

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

if [[ "$LOCAL_SHA" == "$REMOTE_SHA" ]]; then
  echo "Already up to date on $BRANCH ($LOCAL_SHA)."
  exit 0
fi

echo "Update found:"
echo "  local : $LOCAL_SHA"
echo "  remote: $REMOTE_SHA"
echo "Pulling latest code ..."
git pull --ff-only origin "$BRANCH"

if pgrep -u "$USER" -f "home-pi-dashboard|python -m homehub.main" >/dev/null 2>&1; then
  echo "Stopping running dashboard ..."
  pkill -TERM -u "$USER" -f "home-pi-dashboard|python -m homehub.main" || true
  sleep 2
  pkill -KILL -u "$USER" -f "home-pi-dashboard|python -m homehub.main" || true
fi

if [[ -z "${DISPLAY:-}" ]]; then
  export DISPLAY=:0
fi

echo "Restarting dashboard ..."
nohup "$ROOT_DIR/scripts/run_on_pi3.sh" >"$LOG_FILE" 2>&1 &

echo "Dashboard restarted."
echo "Log file: $LOG_FILE"
