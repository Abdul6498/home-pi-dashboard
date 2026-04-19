from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import tomllib

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal environments
    def load_dotenv() -> bool:
        return False


load_dotenv()


@dataclass(frozen=True)
class AppSettings:
    name: str
    fullscreen: bool
    width: int
    height: int


@dataclass(frozen=True)
class ThemeSettings:
    name: str
    font_family: str


@dataclass(frozen=True)
class LocationSettings:
    default_lat: float
    default_lon: float


@dataclass(frozen=True)
class ModuleSettings:
    clock: bool
    weather: bool
    gps: bool
    markets: bool


@dataclass(frozen=True)
class RefreshSettings:
    clock_seconds: int
    weather_seconds: int
    gps_seconds: int
    market_seconds: int


@dataclass(frozen=True)
class PerformanceSettings:
    profile: str
    software_rendering: bool
    render_loop: str
    use_daily_wallpapers: bool
    wallpaper_width: int
    wallpaper_height: int


@dataclass(frozen=True)
class Settings:
    app: AppSettings
    theme: ThemeSettings
    location: LocationSettings
    modules: ModuleSettings
    refresh: RefreshSettings
    performance: PerformanceSettings
    weather_api_key: str


def _read_toml(config_path: Path) -> dict:
    if not config_path.exists():
        return {}
    with config_path.open("rb") as handle:
        return tomllib.load(handle)


def _section(data: dict, key: str) -> dict:
    value = data.get(key, {})
    return value if isinstance(value, dict) else {}


def _value(section_data: dict, key: str, default):
    value = section_data.get(key, default)
    return default if value is None else value


def load_settings(config_path: Path | None = None) -> Settings:
    config_file = config_path or Path(os.getenv("HH_CONFIG", "config/settings.toml"))
    data = _read_toml(config_file)

    app = _section(data, "app")
    theme = _section(data, "theme")
    location = _section(data, "location")
    modules = _section(data, "modules")
    refresh = _section(data, "refresh")
    performance = _section(data, "performance")

    weather_api_key = os.getenv("WEATHER_API_KEY", "").strip()

    return Settings(
        app=AppSettings(
            name=str(_value(app, "name", "Home Pi Dashboard")),
            fullscreen=bool(_value(app, "fullscreen", False)),
            width=int(_value(app, "width", 1024)),
            height=int(_value(app, "height", 600)),
        ),
        theme=ThemeSettings(
            name=str(_value(theme, "name", "crystal")),
            font_family=str(_value(theme, "font_family", "DejaVu Sans")),
        ),
        location=LocationSettings(
            default_lat=float(_value(location, "default_lat", 48.99407)),
            default_lon=float(_value(location, "default_lon", 9.18629)),
        ),
        modules=ModuleSettings(
            clock=bool(_value(modules, "clock", True)),
            weather=bool(_value(modules, "weather", True)),
            gps=bool(_value(modules, "gps", True)),
            markets=bool(_value(modules, "markets", True)),
        ),
        refresh=RefreshSettings(
            clock_seconds=max(1, int(_value(refresh, "clock_seconds", 1))),
            weather_seconds=max(30, int(_value(refresh, "weather_seconds", 900))),
            gps_seconds=max(10, int(_value(refresh, "gps_seconds", 90))),
            market_seconds=max(300, int(_value(refresh, "market_seconds", 3600))),
        ),
        performance=PerformanceSettings(
            profile=str(_value(performance, "profile", "rpi3")),
            software_rendering=bool(_value(performance, "software_rendering", False)),
            render_loop=str(_value(performance, "render_loop", "basic")),
            use_daily_wallpapers=bool(_value(performance, "use_daily_wallpapers", True)),
            wallpaper_width=max(320, int(_value(performance, "wallpaper_width", 1024))),
            wallpaper_height=max(240, int(_value(performance, "wallpaper_height", 600))),
        ),
        weather_api_key=weather_api_key,
    )
