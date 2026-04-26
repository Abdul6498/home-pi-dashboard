# Home Pi Dashboard

Prayer-first smart home dashboard for Raspberry Pi, built with `Python + PySide6/QML`, with live Salah progress integration from a Jetson Nano over UDP.

## Architecture Overview

![Home Pi Dashboard architecture](docs/images/home-pi-dashboard-architecture.png)

## Current UI

![Home Pi Dashboard UI](docs/images/app_home_pi.png)

## What the app does

The dashboard is designed for a `1024x600` touch display and focuses on:

- large fullscreen digital clock
- Gregorian date
- Hijri date with month and year
- current weather and `6`-day forecast
- current prayer and next prayer time
- prayer countdown bar
- adhan playback
- prayer reminder buzzer
- missed prayer notification bell and popup
- live Salah progress and rakat tracking from UDP packets

## Core features

### Prayer features

- current prayer detection
- next prayer name and time
- time-left countdown for the active prayer window
- per-prayer progress bar that changes color as time runs out
- custom reminder rules:
  - `Fajr`: `10` minutes before end of Fajr window
  - `Dhuhr`: `10` minutes before `Asr`
  - `Asr`: `10` minutes before `Maghrib`
  - `Maghrib`: `10` minutes before `Isha`
  - `Isha`: `30` minutes after Isha time, for `5` minutes
- tap reminder area to stop the active reminder
- missed prayer bell appears only when a real reminder was not acknowledged

### Salah progress features

- receives UDP data from another app running on Jetson Nano
- reads:
  - `fsm_state`
  - `current_rakat`
  - `prayer_name`
- maps live FSM states into dashboard stages:
  - `QIYAM`
  - `RUKU`
  - `QAUMA`
  - `SUJUD_1`
  - `JALSA`
  - `SUJUD_2`
  - `TASHAHHUD` / `TASLIM`
- shows live posture progress
- shows current rakat
- tracks skipped/missed states
- marks missed states in red
- preserves per-rakat progress history
- lets you tap a rakat circle to inspect that rakat’s stored progress

### Weather and date features

- current weather from Open-Meteo
- temperature
- humidity
- weather condition icon
- `6`-day forecast
- Hijri date pulled through the prayer-time API flow

### UI features

- fullscreen QML interface
- touch-friendly layout
- black background with transparent bordered cards
- optimized for Raspberry Pi class hardware

## High-level architecture

### Jetson Nano side

The external vision application sends UDP packets over the local network.  
Those packets contain posture and rakat state such as:

- `fsm_state`
- `current_rakat`
- `prayer_name`

### Raspberry Pi side

The dashboard listens for those packets and combines them with:

- prayer timing logic
- weather data
- adhan/reminder audio
- UI state

### Main internal layers

#### 1. Service layer

- `weather_service.py`
  - fetches current weather and forecast from Open-Meteo
- `prayer_time_service.py`
  - computes current prayer, next prayer, Hijri data, and countdowns
- `adhan_audio_service.py`
  - handles adhan and reminder playback with Linux-friendly backends
- `udp_overlay_service.py`
  - listens for UDP packets and parses live Salah state

#### 2. Controller layer

- `qml_app.py`
  - central state manager for the dashboard
  - merges clock, prayer, weather, reminder, notification, and UDP data
  - exposes properties to QML

#### 3. UI layer

- `src/homehub/qml/Main.qml`
  - renders the fullscreen dashboard
  - drives layout, colors, animations, touch behavior

## Project structure

```text
home-pi-dashboard/
  config/
    prayers.json
    settings.example.toml
  docs/
    images/
  scripts/
    install_pi_app.sh
    install_systemd_user_services.sh
    run_dashboard.sh
    run_on_pi3.sh
    update_and_restart_on_pi.sh
  src/homehub/
    assets/
    config.py
    main.py
    qml/
      Main.qml
    qml_app.py
    modules/
    services/
      adhan_audio_service.py
      prayer_time_service.py
      udp_overlay_service.py
      weather_service.py
    ui/
  tests/
```

## Requirements

- Python `3.11+`
- Linux desktop session for GUI
- `PySide6`
- `pygame`
- Raspberry Pi OS 64-bit is the main deployment target

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
cp config/settings.example.toml config/settings.toml
python -m homehub.main
```

Installed command:

```bash
home-pi-dashboard
```

## Configuration

### `config/settings.toml`

Main runtime config lives here.

Important sections:

- `[app]`
  - fullscreen and base resolution
- `[background]`
  - black mode or image mode
- `[location]`
  - fallback coordinates
- `[modules]`
  - enable/disable major sections
- `[refresh]`
  - update intervals
- `[performance]`
  - Pi tuning
- `[udp_overlay]`
  - UDP receiver settings

### `.env`

Current useful `.env` knobs:

```env
# Optional alternate config path
# HH_CONFIG=config/settings.toml

# Temporary adhan test
# HH_TEST_ADHAN_AFTER_SECONDS=15
# HH_TEST_ADHAN_SALAH=Fajr

# Multi-monitor testing on laptop
# HH_TEST_SCREEN=4

# Manual Salah progress fallback values when no UDP is active
# HH_TEST_SALAH_PROGRESS_NAME=Jalsa
# HH_TEST_RAKAT_NUMBER=2

# Optional live UDP overlay
# HH_UDP_OVERLAY_ENABLED=true
# HH_UDP_OVERLAY_HOST=0.0.0.0
# HH_UDP_OVERLAY_PORT=5005
```

## UDP live Salah integration

Enable UDP mode in `.env`:

```env
HH_UDP_OVERLAY_ENABLED=true
HH_UDP_OVERLAY_HOST=0.0.0.0
HH_UDP_OVERLAY_PORT=5005
```

Expected payload shape contains data like:

```json
{
  "event": "overlay_frame",
  "prayer_name": "Fajr / Sunnah / Nafl",
  "current_rakat": 1,
  "fsm_state": "QIYAM"
}
```

Notes:

- the dashboard extracts JSON even if the UDP packet has binary bytes before the payload
- if UDP stops, the dashboard keeps the last live state briefly
- after timeout, it falls back to non-live dashboard behavior

## Raspberry Pi setup

Before first launch on Raspberry Pi OS, install the Qt/X11 runtime packages used by PySide6:

```bash
sudo apt update
sudo apt install -y libxcb-cursor0 libxkbcommon-x11-0
```

If you see:

```text
qt.qpa.plugin: From 6.5.0, xcb-cursor0 or libxcb-cursor0 is needed to load the Qt xcb platform plugin
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
```

those packages are missing.

## Run on Raspberry Pi

```bash
cd /path/to/home-pi-dashboard
./scripts/run_on_pi3.sh
```

What it does:

- creates `.venv` if needed
- installs or updates the package
- copies `.env.example` if `.env` is missing
- copies `config/settings.example.toml` if `config/settings.toml` is missing
- launches the dashboard

## Auto-update and restart on Pi

```bash
cd /path/to/home-pi-dashboard
./scripts/update_and_restart_on_pi.sh
```

Behavior:

- fetches `origin/main`
- fast-forwards local branch if needed
- restarts the dashboard if new code arrived
- starts the app if it is not already running

## systemd user services on Pi

```bash
cd /path/to/home-pi-dashboard
./scripts/install_systemd_user_services.sh
```

This installs:

- `home-pi-dashboard.service`
- `home-pi-dashboard-update.service`
- `home-pi-dashboard-update.timer`

Useful commands:

```bash
systemctl --user status home-pi-dashboard.service
systemctl --user restart home-pi-dashboard.service
systemctl --user status home-pi-dashboard-update.timer
journalctl --user -u home-pi-dashboard.service -f
```

## App-style install on Pi

```bash
cd /path/to/home-pi-dashboard
./scripts/install_pi_app.sh
```

This creates:

- `~/.local/bin/home-pi-dashboard`
- `~/.local/share/applications/home-pi-dashboard.desktop`

## Audio notes

Adhan and reminder playback use multiple Linux-friendly backends.  
The app can use available tools such as:

- `ffplay`
- `cvlc`
- `pygame`

This helps keep playback working across WSL, Ubuntu desktops, and Raspberry Pi environments.

## Troubleshooting

### App opens on the wrong monitor

Use:

```env
HH_TEST_SCREEN=4
```

This is mainly for laptop multi-display testing before deploying to Pi.

### UDP is enabled but nothing moves

Check:

- sender is using the same port
- packets are reaching the Pi/laptop
- `fsm_state` values match supported states

### Reminder / adhan test

Use:

```env
HH_TEST_ADHAN_AFTER_SECONDS=15
HH_TEST_ADHAN_SALAH=Fajr
```

Then restart the app.

## Roadmap direction

Planned next growth areas:

- stronger Jetson Nano / SalahSense integration
- richer fallback and review modes
- home widgets and modular cards
- more production polish for kiosk deployments
