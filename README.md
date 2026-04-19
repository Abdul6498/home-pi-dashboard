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

## Why this architecture

This project is intentionally modular so each feature can be built as an independent module and plugged into the main app without rewriting everything.

## Tech choice (v1)

- Language: Python 3.11+
- UI: Tkinter (lightweight and included with Python)
- Data services: modular service classes (weather, GPS, time)
- Config: environment variables via `.env`
- Tests: pytest

This keeps deployment simple on Raspberry Pi 3 while still allowing advanced visuals and future migration to a web UI if needed.

## Project structure

```text
home-pi-dashboard/
  docs/
    ARCHITECTURE.md
    ROADMAP.md
  src/homehub/
    main.py
    config.py
    modules/
      clock.py
      weather.py
      gps.py
    services/
      weather_service.py
      gps_service.py
    ui/
      theme.py
  tests/
    test_config.py
```

## Quick start (local dev)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
python -m homehub.main
```

## Raspberry Pi run mode (planned)

- Launch full-screen at boot
- Hide window controls/cursor
- Refresh weather periodically
- Offline-safe fallback for GPS/weather APIs

## Next milestone

Build a polished full-screen home screen with:
- live clock
- date
- city/location from GPS
- weather summary and icon text
- themed gradient background + readable overlays
