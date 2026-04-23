from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import os
import platform
import sys

from homehub.config import load_settings
from homehub.modules.clock import ClockModule
from homehub.modules.gps import GPSModule
from homehub.modules.weather import WeatherModule
from homehub.services.daily_seasonal_image_service import DailySeasonalImageService
from homehub.services.adhan_audio_service import AdhanAudioService
from homehub.services.gps_service import GPSService
from homehub.services.market_price_service import MarketPriceService
from homehub.services.prayer_time_service import PrayerTimeService
from homehub.services.weather_service import WeatherService
from homehub.ui.backgrounds import (
    bundled_background_path,
    prepare_background_asset,
    resolve_background_path,
)
from homehub.ui.seasonal import season_for_now

try:
    from PySide6.QtCore import QObject, Property, QTimer, Signal, Qt, Slot
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
        self.adhan_audio = AdhanAudioService()

        self._time_text = "--:--"
        self._seconds_text = "--"
        self._period_text = "--"
        self._weekday_text = "---"
        self._date_text = "--- --"
        self._year_text = "----"
        self._app_fullscreen = self.settings.app.fullscreen

        self._weather_icon = "☁"
        self._weather_icon_color = "#68c8ff"
        self._weather_condition_kind = "cloudy"
        self._weather_summary = "--"
        self._temperature_text = "--C"
        self._humidity_text = "--%"
        self._uv_text = "UV --"

        self._location_name = "Hessigheim"

        self._next_salah_text = "--"
        self._time_left_text = "--H --M"
        self._current_salah_text = "--"
        self._prayer_alert_threshold_minutes = max(
            1, int(os.getenv("HH_PRAYER_ALERT_MINUTES", "10") or "10")
        )
        self._force_prayer_alert = (
            os.getenv("HH_FORCE_PRAYER_ALERT", "").strip().lower() in {"1", "true", "yes", "on"}
        )
        self._prayer_alert_active = False
        self._prayer_alert_marker = ""
        self._dismissed_prayer_alert_marker = ""
        self._auto_closed_prayer_alert_marker = ""
        self._missed_prayer_items: list[str] = []
        self._missed_prayer_count = 0
        self._missed_prayer_overlay_visible = False

        self._forecast_items: list[dict] = []
        self._market_items: list[dict] = []
        self._crypto_items: list[dict] = []
        self._stock_items: list[dict] = []
        self._background_image_url = self._pick_background_url()
        self._background_day = datetime.now().date()
        self._last_adhan_marker = ""
        self._active_adhan_marker = ""
        self._post_adhan_image_url = self._pick_post_adhan_image_url()
        self._post_adhan_visible_until: datetime | None = None

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(max(1000, self.settings.refresh.clock_seconds * 1000))

        self._weather_counter = 0
        self._gps_counter = 0
        self._market_counter = 0
        self.refresh(force=True)

    def shutdown(self) -> None:
        self._timer.stop()
        self._active_adhan_marker = ""
        self._post_adhan_visible_until = None
        self.adhan_audio.stop()

    def refresh(self, force: bool = False) -> None:
        now = datetime.now()
        clock_data = self.clock.update()
        self._time_text = clock_data.time_text
        self._seconds_text = clock_data.seconds_text
        self._period_text = clock_data.period_text
        self._weekday_text = clock_data.weekday_text
        self._date_text = clock_data.date_text
        self._year_text = now.strftime("%Y")

        if self._background_day != now.date():
            self._background_day = now.date()
            self._background_image_url = self._pick_background_url()
            self._missed_prayer_items = []
            self._missed_prayer_count = 0
            self._missed_prayer_overlay_visible = False

        interval = max(1, self.settings.refresh.clock_seconds)
        self._weather_counter += interval
        self._gps_counter += interval
        self._market_counter += interval

        if force or self._weather_counter >= self.settings.refresh.weather_seconds:
            weather_data = self.weather.update()
            icon, icon_color = self._icon_for_condition(weather_data.condition_kind)
            self._weather_icon = icon
            self._weather_icon_color = icon_color
            self._weather_condition_kind = weather_data.condition_kind
            self._weather_summary = weather_data.summary
            self._temperature_text = f"{weather_data.temperature_c}\N{DEGREE SIGN} C"
            self._humidity_text = f"{weather_data.humidity_pct}%"
            self._uv_text = f"UV {weather_data.uv_index}"
            self._forecast_items = [
                {
                    "day": day.day_label,
                    "iconKind": day.icon_kind,
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

        prayer = self.prayer.get_status(now)
        self._current_salah_text = self._display_salah_name(prayer.current_salah).upper()
        next_display = self._display_salah_name(prayer.next_salah)
        self._next_salah_text = f"{next_display} {prayer.next_time_text}".upper()
        self._time_left_text = f"{prayer.time_left_text} LEFT".upper()
        was_alert_active = self._prayer_alert_active
        current_is_isha = prayer.current_salah.strip().lower() == "isha"
        if current_is_isha and prayer.next_time_moment is not None:
            isha_event_day = prayer.next_time_moment.date() - timedelta(days=1)
            marker = f"Isha|{isha_event_day.isoformat()}"
        elif current_is_isha:
            marker = f"Isha|{now.date().isoformat()}"
        else:
            marker_moment = (
                prayer.next_time_moment.isoformat() if prayer.next_time_moment else prayer.next_time_text
            )
            marker = f"{prayer.next_salah}|{marker_moment}"
        if marker != self._prayer_alert_marker:
            missed_name_override = (
                prayer.current_salah
                if self._is_trackable_prayer_name(prayer.current_salah)
                else None
            )
            self._mark_prayer_missed_if_unacknowledged(
                self._prayer_alert_marker,
                prayer_name_override=missed_name_override,
            )
            self._prayer_alert_marker = marker
            self._prayer_alert_active = False
        should_alert = (
            prayer.next_salah != "N/A"
            and prayer.next_salah != "Imsak"
            and 0 <= prayer.time_left_minutes <= self._prayer_alert_threshold_minutes
        )
        if self._force_prayer_alert:
            should_alert = prayer.next_salah not in {"N/A", "Imsak"}

        if current_is_isha:
            should_alert = self.prayer.isha_reminder_window_active(
                now,
                offset_minutes=30,
                duration_minutes=5,
            )
        should_auto_stop = (
            prayer.next_salah != "N/A"
            and prayer.next_salah != "Imsak"
            and not self._force_prayer_alert
            and 0 <= prayer.time_left_minutes <= 1
        )
        if should_auto_stop:
            self._mark_prayer_missed_if_unacknowledged(self._prayer_alert_marker)
            self._prayer_alert_active = False
        elif current_is_isha:
            self._prayer_alert_active = should_alert
            if was_alert_active and not self._prayer_alert_active:
                self._mark_prayer_missed_if_unacknowledged(self._prayer_alert_marker)
        else:
            self._prayer_alert_active = (
                should_alert and self._dismissed_prayer_alert_marker != self._prayer_alert_marker
                and self._auto_closed_prayer_alert_marker != self._prayer_alert_marker
            )
        if self._prayer_alert_active:
            self.adhan_audio.start_prayer_reminder()
        else:
            self.adhan_audio.stop_prayer_reminder()
        self._play_adhan_if_due(now)
        self._update_post_adhan_image_state(now)

        self.dataChanged.emit()

    def _pick_background_url(self) -> str:
        if not self.settings.background.enabled:
            return ""
        if self.settings.background.mode == "black":
            return ""

        season = season_for_now()
        cache_dir = self.daily_images.cache_dir() / "optimized"
        source_path: Path | None = None

        if self.settings.background.use_daily_image:
            source_path = self.daily_images.get_daily_image_path(season.name)

        if source_path is None:
            source_path = resolve_background_path(self.settings.background.default_image)

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

    def _display_salah_name(self, salah_name: str) -> str:
        key = salah_name.strip().lower()
        if key == "before fajr":
            return "Isha"
        if key == "dhuhr":
            return "Duhur"
        if key == "maghrib":
            return "Maghrib"
        return salah_name

    def _mark_prayer_missed_if_unacknowledged(
        self,
        marker: str,
        *,
        prayer_name_override: str | None = None,
    ) -> None:
        if not marker:
            return
        if marker == self._dismissed_prayer_alert_marker:
            return
        if marker == self._auto_closed_prayer_alert_marker:
            return
        self._auto_closed_prayer_alert_marker = marker
        prayer_name = (
            self._display_salah_name(prayer_name_override).upper()
            if prayer_name_override
            else self._missed_prayer_name_from_marker(marker)
        )
        if prayer_name:
            self._missed_prayer_items.append(prayer_name)
        self._missed_prayer_count += 1

    def _is_trackable_prayer_name(self, prayer_name: str) -> bool:
        key = prayer_name.strip().lower()
        return key in {"fajr", "dhuhr", "asr", "maghrib", "isha"}

    def _missed_prayer_name_from_marker(self, marker: str) -> str:
        prayer_key = marker.split("|", 1)[0].strip()
        return self._display_salah_name(prayer_key).upper() if prayer_key else ""

    def _pick_post_adhan_image_url(self) -> str:
        asset_roots = [
            Path(__file__).resolve().parents[1] / "assets",
            Path(__file__).resolve().parents[2] / "assets",
        ]
        for assets_dir in asset_roots:
            if not assets_dir.exists():
                continue
            for pattern in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
                for path in sorted(assets_dir.glob(pattern)):
                    return path.resolve().as_uri()
            for pattern in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
                for path in sorted(assets_dir.rglob(pattern)):
                    if "seasonal" in path.parts:
                        continue
                    return path.resolve().as_uri()
        return ""

    def _play_adhan_if_due(self, now: datetime) -> None:
        salah_name = self.prayer.due_salah_for_adhan(now)
        if salah_name is None:
            return
        marker = f"{now.date().isoformat()}:{salah_name}"
        if marker == self._last_adhan_marker:
            return
        if self.adhan_audio.play_for_salah(salah_name):
            self._last_adhan_marker = marker
            self._active_adhan_marker = marker

    def _update_post_adhan_image_state(self, now: datetime) -> None:
        if self._active_adhan_marker and not self.adhan_audio.is_playing():
            if self._post_adhan_image_url:
                self._post_adhan_visible_until = now + timedelta(minutes=1)
            self._active_adhan_marker = ""

        if self._post_adhan_visible_until and now >= self._post_adhan_visible_until:
            self._post_adhan_visible_until = None

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
    def weatherConditionKind(self) -> str:
        return self._weather_condition_kind

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

    @Property(bool, notify=dataChanged)
    def prayerAlertActive(self) -> bool:
        return self._prayer_alert_active

    @Property(bool, notify=dataChanged)
    def missedPrayerNotificationVisible(self) -> bool:
        return self._missed_prayer_count > 0

    @Property(int, notify=dataChanged)
    def missedPrayerCount(self) -> int:
        return self._missed_prayer_count

    @Property("QVariantList", notify=dataChanged)
    def missedPrayerItems(self) -> list[str]:
        return self._missed_prayer_items

    @Property(bool, notify=dataChanged)
    def missedPrayerOverlayVisible(self) -> bool:
        return self._missed_prayer_overlay_visible and bool(self._missed_prayer_items)

    @Slot()
    def acknowledgePrayerAlert(self) -> None:
        self._dismissed_prayer_alert_marker = self._prayer_alert_marker
        self._prayer_alert_active = False
        self.adhan_audio.stop_prayer_reminder()
        self.dataChanged.emit()

    @Slot()
    def clearMissedPrayerNotifications(self) -> None:
        self._missed_prayer_count = 0
        self._missed_prayer_items = []
        self._missed_prayer_overlay_visible = False
        self.dataChanged.emit()

    @Slot()
    def showMissedPrayerOverlay(self) -> None:
        if not self._missed_prayer_items:
            return
        self._missed_prayer_overlay_visible = True
        self.dataChanged.emit()

    @Slot()
    def hideMissedPrayerOverlay(self) -> None:
        self._missed_prayer_overlay_visible = False
        self.dataChanged.emit()

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

    @Property(bool, notify=dataChanged)
    def appFullscreen(self) -> bool:
        return self._app_fullscreen

    @Property(str, notify=dataChanged)
    def postAdhanImageUrl(self) -> str:
        return self._post_adhan_image_url

    @Property(bool, notify=dataChanged)
    def showPostAdhanImage(self) -> bool:
        return (
            self._post_adhan_visible_until is not None
            and datetime.now() < self._post_adhan_visible_until
            and bool(self._post_adhan_image_url)
        )


def run() -> int:
    settings = load_settings()
    _configure_qt_backend(settings)
    app = QGuiApplication(sys.argv)
    controller = DashboardController()
    app.aboutToQuit.connect(controller.shutdown)

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("dashboard", controller)

    qml_path = Path(__file__).with_name("qml") / "Main.qml"
    engine.load(str(qml_path))

    if not engine.rootObjects():
        return 1
    window = engine.rootObjects()[0]
    window.setFlags(window.flags() | Qt.FramelessWindowHint)
    if settings.app.fullscreen:
        window.setX(0)
        window.setY(0)
        window.showFullScreen()
    else:
        window.show()
    return app.exec()


def _configure_qt_backend(settings) -> None:
    # Use conservative defaults for Pi-class hardware while forcing software mode on WSL.
    is_wsl = "microsoft" in platform.release().lower()
    os.environ.setdefault("NO_AT_BRIDGE", "1")
    os.environ.setdefault("QT_LINUX_ACCESSIBILITY_ALWAYS_OFF", "1")
    if is_wsl or settings.performance.software_rendering:
        os.environ.setdefault("QT_QUICK_BACKEND", "software")
        os.environ.setdefault("QSG_RHI_BACKEND", "software")
    else:
        os.environ.setdefault("QSG_RENDER_LOOP", settings.performance.render_loop)
