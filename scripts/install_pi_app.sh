#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="$HOME/.local/share/home-pi-dashboard"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

mkdir -p "$APP_DIR" "$BIN_DIR" "$DESKTOP_DIR"

echo "Syncing project into $APP_DIR ..."
rsync -a \
  --delete \
  --exclude ".git" \
  --exclude ".venv" \
  --exclude "__pycache__" \
  --exclude ".pytest_cache" \
  --exclude "assets/seasonal/daily/optimized" \
  "$ROOT_DIR"/ "$APP_DIR"/

chmod +x "$APP_DIR/scripts/run_on_pi3.sh"

cat > "$BIN_DIR/home-pi-dashboard" <<EOF
#!/usr/bin/env bash
exec "$APP_DIR/scripts/run_on_pi3.sh"
EOF
chmod +x "$BIN_DIR/home-pi-dashboard"

cat > "$DESKTOP_DIR/home-pi-dashboard.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Home Pi Dashboard
Comment=Launch the Raspberry Pi home dashboard
Exec=$BIN_DIR/home-pi-dashboard
Terminal=false
Categories=Utility;
EOF

echo
echo "Installed launcher:"
echo "  $BIN_DIR/home-pi-dashboard"
echo
echo "Desktop entry:"
echo "  $DESKTOP_DIR/home-pi-dashboard.desktop"
echo
echo "Run it with:"
echo "  home-pi-dashboard"
