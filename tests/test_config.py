from pathlib import Path

from homehub.config import load_settings


def test_load_settings_defaults(tmp_path: Path) -> None:
    settings = load_settings(tmp_path / "missing.toml")
    assert settings.theme.name == "crystal"
    assert settings.background.enabled is True
    assert settings.background.use_daily_image is True
    assert settings.background.default_image == "spring.jpg"
    assert settings.refresh.weather_seconds == 900
    assert settings.refresh.market_seconds == 3600
    assert settings.modules.clock is True
    assert settings.modules.markets is True
    assert round(settings.location.default_lat, 5) == 48.99407
    assert round(settings.location.default_lon, 5) == 9.18629
    assert settings.performance.profile == "rpi3"
    assert settings.performance.wallpaper_width == 1024


def test_load_settings_from_toml(tmp_path: Path) -> None:
    config_file = tmp_path / "settings.toml"
    config_file.write_text(
        """
[app]
name = "Home Wall"
fullscreen = true
width = 1280
height = 720

[theme]
name = "sunrise"
font_family = "Noto Sans"

[background]
enabled = true
use_daily_image = false
default_image = "assets/seasonal/winter.jpg"

[location]
default_lat = 24.8607
default_lon = 67.0011

[modules]
clock = true
weather = false
gps = true
markets = false

[refresh]
clock_seconds = 1
weather_seconds = 600
gps_seconds = 30
market_seconds = 7200

[performance]
profile = "desktop"
software_rendering = true
render_loop = "basic"
use_daily_wallpapers = false
wallpaper_width = 1280
wallpaper_height = 720
""".strip(),
        encoding="utf-8",
    )

    settings = load_settings(config_file)
    assert settings.app.name == "Home Wall"
    assert settings.app.fullscreen is True
    assert settings.theme.name == "sunrise"
    assert settings.background.use_daily_image is False
    assert settings.background.default_image == "assets/seasonal/winter.jpg"
    assert settings.location.default_lat == 24.8607
    assert settings.modules.weather is False
    assert settings.modules.markets is False
    assert settings.refresh.gps_seconds == 30
    assert settings.refresh.market_seconds == 7200
    assert settings.performance.software_rendering is True
    assert settings.performance.use_daily_wallpapers is False


def test_load_settings_background_uses_legacy_performance_flag(tmp_path: Path) -> None:
    config_file = tmp_path / "settings.toml"
    config_file.write_text(
        """
[performance]
use_daily_wallpapers = false
""".strip(),
        encoding="utf-8",
    )

    settings = load_settings(config_file)
    assert settings.background.use_daily_image is False
