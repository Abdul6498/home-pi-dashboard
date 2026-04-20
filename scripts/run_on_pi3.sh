#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but was not found."
  exit 1
fi

if command -v dpkg >/dev/null 2>&1; then
  missing_packages=()
  for pkg in libxcb-cursor0 libxkbcommon-x11-0; do
    if ! dpkg -s "$pkg" >/dev/null 2>&1; then
      missing_packages+=("$pkg")
    fi
  done

  if (( ${#missing_packages[@]} > 0 )); then
    echo "Missing Qt runtime packages: ${missing_packages[*]}"
    echo "Install them with:"
    echo "  sudo apt update && sudo apt install -y ${missing_packages[*]}"
    exit 1
  fi
fi

ARCH="$(uname -m)"
if [[ "$ARCH" != "aarch64" && "$ARCH" != "x86_64" ]]; then
  cat <<'EOF'
This launcher works best on 64-bit Raspberry Pi OS.
Detected architecture is not 64-bit, and PySide6 may fail to install on 32-bit systems.
Recommended: use Raspberry Pi OS 64-bit on Raspberry Pi 3.
EOF
fi

if [[ ! -d ".venv" ]]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing/updating dashboard package..."
python -m pip install --upgrade pip
python -m pip install -e .

if [[ ! -f ".env" && -f ".env.example" ]]; then
  cp .env.example .env
fi

if [[ ! -f "config/settings.toml" && -f "config/settings.example.toml" ]]; then
  cp config/settings.example.toml config/settings.toml
fi

export QSG_RENDER_LOOP="${QSG_RENDER_LOOP:-basic}"

echo "Launching Home Pi Dashboard..."
exec .venv/bin/home-pi-dashboard
