# Home Pi Dashboard

A modular Raspberry Pi 3 home dashboard designed for a 7-inch HDMI display.

## Vision

Start with a beautiful full-screen clock and weather panel, then grow into a smart home wall dashboard with modular features.

Planned feature modules:
- clock (phase 1)
- weather (phase 1)
- GPS/location-aware updates (phase 1)
- calendar (phase 2)
- home automation widgets (phase 2)
- prayer/azan and reminders (phase 2)
- local media/news cards (phase 3)

## Stack direction

- Language: Python 3.11+
- GUI strategy: Qt/QML (PySide6) for a clean 1024x600 production layout
- Data services: modular service classes (weather, GPS, time)
- Config: TOML settings + `.env` secrets
- Tests: pytest

The default profile is tuned for Raspberry Pi 3:
- basic Qt render loop
- display-sized wallpaper derivatives instead of full-resolution originals
- optional cached daily wallpaper downloads with local fallback

## Settings-first foundation

The app now supports profile-style settings from `config/settings.toml` (see `config/settings.example.toml`).

Config includes:
- app window/fullscreen sizing
- theme + font family
- module toggles (`clock`, `weather`, `gps`)
- refresh intervals per module
- fallback coordinates (defaulted to Hessigheim, Germany)
- performance profile (`rpi3`) and wallpaper/rendering options

Secrets stay in `.env` (for example `WEATHER_API_KEY`).

## Project structure

```text
home-pi-dashboard/
  config/
    settings.example.toml
  docs/
    ARCHITECTURE.md
    ROADMAP.md
  src/homehub/
    main.py
    qml_app.py
    config.py
    modules/
      clock.py
      weather.py
      gps.py
    services/
      weather_service.py
      gps_service.py
    ui/
      seasonal.py
    qml/
      Main.qml
  tests/
    test_config.py
```

## Quick start (local dev)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
cp config/settings.example.toml config/settings.toml
python -m homehub.main
```

Weather data is fetched live from Open-Meteo and rendered with condition-aware icon styling.
Default style now uses the `crystal` theme and automatic seasonal visuals (spring/summer/autumn/winter).
Real seasonal image assets are stored in `assets/seasonal/` with attribution in `assets/seasonal/ATTRIBUTION.md`.
The app can also fetch one daily seasonal wallpaper from Wikimedia Commons into `assets/seasonal/daily/` (with per-image attribution JSON), then fall back to bundled assets when offline.

## WSL GUI Run Notes

Use the launcher from a normal WSL shell (do not use `sudo`):

```bash
cd /home/user/Workspace/home-pi-dashboard
./scripts/run_dashboard.sh
```

If you see `libEGL`/`MESA`/`Vulkan` warnings in WSL, the app now defaults Qt to software rendering (`QT_QUICK_BACKEND=software` and `QSG_RHI_BACKEND=software`) to keep GUI rendering stable.

If this is your first run:

```bash
cd /home/user/Workspace/home-pi-dashboard
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
./scripts/run_dashboard.sh
```
