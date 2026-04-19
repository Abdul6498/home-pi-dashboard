#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d ".venv" ]]; then
  echo "Missing .venv. Run: python3 -m venv .venv && source .venv/bin/activate && pip install -e .[dev]"
  exit 1
fi

source .venv/bin/activate

if [[ -z "${DISPLAY:-}" ]]; then
  echo "DISPLAY is not set. If you are on WSL, open a regular WSL terminal (not sudo/cron) and retry."
  exit 1
fi

export QSG_RENDER_LOOP="${QSG_RENDER_LOOP:-basic}"

python -m homehub.main
