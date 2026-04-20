from __future__ import annotations

from datetime import datetime
from pathlib import Path
import os
import platform
import sys

from homehub.config import load_settings
from homehub.modules.clock import ClockModule
from homehub.modules.gps import GPSModule
from homehub.modules.weather import WeatherModule
from homehub.services.daily_seasonal_image_service import DailySeasonalImageService
from homehub.services.gps_service import GPSService
from homehub.services.market_price_service import MarketPriceService
from homehub.services.prayer_time_service import PrayerTimeService
from homehub.services.weather_service import WeatherService
from homehub.ui.backgrounds import bundled_background_path, prepare_background_asset
from homehub.ui.seasonal import season_for_now

try:
    from PySide6.QtCore import QObject, Property, QTimer, Signal
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine
except ModuleNotFoundError as exc:  # pragma: no cover
    raise RuntimeError(
        "PySide6 is required for the QML UI. Install with: pip install -e .[dev]"
    ) from exc


class DashboardController(QObject):
    dataChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.settings = load_settings()
        self.clock = ClockModule()
        self.weather = WeatherModule(WeatherService(self.settings.weather_api_key))
        self.gps = GPSModule(
            GPSService(
                self.settings.location.default_lat,
                self.settings.location.default_lon,
            )
        )
        self.prayer = PrayerTimeService(
            city="Hessigheim",
            country="Germany",
            latitude=self.settings.location.default_lat,
            longitude=self.settings.location.default_lon,
        )
        self.daily_images = DailySeasonalImageService()
        self.markets = MarketPriceService()

        self._time_text = "--:--"
        self._seconds_text = "--"
        self._period_text = "--"
        self._weekday_text = "---"
        self._date_text = "--- --"
        self._year_text = "----"

        self._weather_icon = "☁"
        self._weather_icon_color = "#68c8ff"
        self._weather_summary = "--"
        self._temperature_text = "--C"
        self._humidity_text = "--%"
        self._uv_text = "UV --"

        self._location_name = "Hessigheim"

        self._next_salah_text = "--"
        self._time_left_text = "--H --M"
        self._current_salah_text = "--"

        self._forecast_items: list[dict] = []
        self._market_items: list[dict] = []
        self._crypto_items: list[dict] = []
        self._stock_items: list[dict] = []
        self._background_image_url = self._pick_background_url()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(max(1000, self.settings.refresh.clock_seconds * 1000))

        self._weather_counter = 0
        self._gps_counter = 0
        self._market_counter = 0
        self.refresh(force=True)

    def refresh(self, force: bool = False) -> None:
        clock_data = self.clock.update()
        self._time_text = clock_data.time_text
        self._seconds_text = clock_data.seconds_text
        self._period_text = clock_data.period_text
        self._weekday_text = clock_data.weekday_text
        self._date_text = clock_data.date_text
        self._year_text = datetime.now().strftime("%Y")

        interval = max(1, self.settings.refresh.clock_seconds)
        self._weather_counter += interval
        self._gps_counter += interval
        self._market_counter += interval

        if force or self._weather_counter >= self.settings.refresh.weather_seconds:
            weather_data = self.weather.update()
            icon, icon_color = self._icon_for_condition(weather_data.condition_kind)
            self._weather_icon = icon
            self._weather_icon_color = icon_color
            self._weather_summary = weather_data.summary
            self._temperature_text = f"{weather_data.temperature_c}\N{DEGREE SIGN} C"
            self._humidity_text = f"{weather_data.humidity_pct}%"
            self._uv_text = f"UV {weather_data.uv_index}"
            self._forecast_items = [
                {
                    "day": day.day_label,
                    "icon": day.icon,
                    "iconColor": day.icon_color,
                    "high": f"HI {day.high_c}\N{DEGREE SIGN} C",
                    "low": f"LO {day.low_c}\N{DEGREE SIGN} C",
                }
                for day in weather_data.forecast
            ]
            self._weather_counter = 0

        if force or self._gps_counter >= self.settings.refresh.gps_seconds:
            gps_data = self.gps.update()
            self._location_name = gps_data.location_name
            self._gps_counter = 0

        if self.settings.modules.markets and (
            force or self._market_counter >= self.settings.refresh.market_seconds
        ):
            self._market_items = self.markets.fetch_prices()
            self._crypto_items = [
                item for item in self._market_items if item.get("section") == "CRYPTO"
            ]
            self._stock_items = [
                item for item in self._market_items if item.get("section") == "STOCK"
            ]
            self._market_counter = 0

        prayer = self.prayer.get_status(datetime.now())
        self._current_salah_text = prayer.current_salah.upper()
        self._next_salah_text = f"{prayer.next_salah} {prayer.next_time_text}".upper()
        self._time_left_text = f"{prayer.time_left_text} LEFT".upper()

        self.dataChanged.emit()

    def _pick_background_url(self) -> str:
        season = season_for_now()
        cache_dir = self.daily_images.cache_dir() / "optimized"
        source_path: Path | None = None

        if self.settings.performance.use_daily_wallpapers:
            source_path = self.daily_images.get_daily_image_path(season.name)

        if source_path is None:
            bundled = bundled_background_path(season.background_asset)
            if bundled.exists():
                source_path = bundled

        if source_path is not None:
            optimized = prepare_background_asset(
                source_path=source_path,
                cache_dir=cache_dir,
                width=self.settings.performance.wallpaper_width,
                height=self.settings.performance.wallpaper_height,
            )
            if optimized is not None:
                return optimized.resolve().as_uri()
            return source_path.resolve().as_uri()
        return ""

    def _icon_for_condition(self, condition: str) -> tuple[str, str]:
        if condition == "clear":
            return "☀", "#ffd34d"
        if condition == "partly_cloudy":
            return "⛅", "#ffd34d"
        if condition == "cloudy":
            return "☁", "#68c8ff"
        if condition == "fog":
            return "〰", "#9eb3c9"
        if condition == "rainy":
            return "☂", "#62c2ff"
        if condition == "snowy":
            return "❄", "#d8ecff"
        if condition == "storm":
            return "⚡", "#ffd34d"
        return "☁", "#68c8ff"

    @Property(str, notify=dataChanged)
    def timeText(self) -> str:
        return self._time_text

    @Property(str, notify=dataChanged)
    def periodText(self) -> str:
        return self._period_text

    @Property(str, notify=dataChanged)
    def secondsText(self) -> str:
        return self._seconds_text

    @Property(str, notify=dataChanged)
    def weekdayText(self) -> str:
        return self._weekday_text

    @Property(str, notify=dataChanged)
    def dateText(self) -> str:
        return self._date_text

    @Property(str, notify=dataChanged)
    def yearText(self) -> str:
        return self._year_text

    @Property(str, notify=dataChanged)
    def weatherIcon(self) -> str:
        return self._weather_icon

    @Property(str, notify=dataChanged)
    def weatherIconColor(self) -> str:
        return self._weather_icon_color

    @Property(str, notify=dataChanged)
    def weatherSummary(self) -> str:
        return self._weather_summary

    @Property(str, notify=dataChanged)
    def temperatureText(self) -> str:
        return self._temperature_text

    @Property(str, notify=dataChanged)
    def humidityText(self) -> str:
        return self._humidity_text

    @Property(str, notify=dataChanged)
    def uvText(self) -> str:
        return self._uv_text

    @Property(str, notify=dataChanged)
    def locationName(self) -> str:
        return self._location_name

    @Property(str, notify=dataChanged)
    def nextSalahText(self) -> str:
        return self._next_salah_text

    @Property(str, notify=dataChanged)
    def timeLeftText(self) -> str:
        return self._time_left_text

    @Property(str, notify=dataChanged)
    def currentSalahText(self) -> str:
        return self._current_salah_text

    @Property("QVariantList", notify=dataChanged)
    def forecastItems(self) -> list[dict]:
        return self._forecast_items

    @Property("QVariantList", notify=dataChanged)
    def marketItems(self) -> list[dict]:
        return self._market_items

    @Property("QVariantList", notify=dataChanged)
    def cryptoItems(self) -> list[dict]:
        return self._crypto_items

    @Property("QVariantList", notify=dataChanged)
    def stockItems(self) -> list[dict]:
        return self._stock_items

    @Property(str, notify=dataChanged)
    def backgroundImageUrl(self) -> str:
        return self._background_image_url


def run() -> int:
    settings = load_settings()
    _configure_qt_backend(settings)
    app = QGuiApplication(sys.argv)
    controller = DashboardController()

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("dashboard", controller)

    qml_path = Path(__file__).with_name("qml") / "Main.qml"
    engine.load(str(qml_path))

    if not engine.rootObjects():
        return 1
    return app.exec()


def _configure_qt_backend(settings) -> None:
    # Use conservative defaults for Pi-class hardware while forcing software mode on WSL.
    is_wsl = "microsoft" in platform.release().lower()
    if is_wsl or settings.performance.software_rendering:
        os.environ.setdefault("QT_QUICK_BACKEND", "software")
        os.environ.setdefault("QSG_RHI_BACKEND", "software")
    else:
        os.environ.setdefault("QSG_RENDER_LOOP", settings.performance.render_loop)
