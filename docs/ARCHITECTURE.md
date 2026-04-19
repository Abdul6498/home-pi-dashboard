# Architecture

## Goals

1. Keep features independent and pluggable.
2. Keep Pi runtime lightweight.
3. Support graceful offline behavior.
4. Support future move to richer UI without throwing away service logic.

## High-level design

- `main.py` bootstraps app and render loop.
- `config.py` loads environment and app settings.
- `modules/*` define presentation-facing modules (clock, weather, gps).
- `services/*` define data adapters (API calls, device integrations).
- `services/daily_seasonal_image_service.py` fetches/caches one free seasonal wallpaper per day from Wikimedia Commons.
- `ui/palette.py` centralizes color palette presets.
- `ui/components.py` provides reusable dashboard widget components.
- `ui/seasonal.py` provides season-based visual accents and decorative strips.
- `ui/backgrounds.py` loads and crops seasonal photo assets for the dashboard hero strip.

## Module contract (v1)

Each module should expose:
- `update()` for fetching/refreshing state
- `snapshot()` for returning data safe to render

## Update cadence strategy

- clock: every second
- gps: every 60-120 seconds
- weather: every 10-15 minutes

## Future extension points

- event bus for inter-module communication
- persistent cache for last known weather/location
- plugin registry for optional modules
