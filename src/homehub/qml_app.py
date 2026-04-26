from __future__ import annotations

from datetime import datetime, timedelta
import json
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
from homehub.services.udp_overlay_service import UdpOverlayService
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
    _SALAH_PROGRESS_STAGE_KEYS = (
        "qiyam",
        "ruku",
        "itidal",
        "sajda_1",
        "jalsa",
        "sajda_2",
        "taslim",
    )

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
        self.udp_overlay = UdpOverlayService(
            enabled=self.settings.udp_overlay.enabled,
            bind_host=self.settings.udp_overlay.bind_host,
            port=self.settings.udp_overlay.port,
        )

        self._time_text = "--:--"
        self._seconds_text = "--"
        self._period_text = "--"
        self._weekday_text = "---"
        self._date_text = "--- --"
        self._year_text = "----"
        self._app_fullscreen = True

        self._weather_icon = "☁"
        self._weather_icon_color = "#68c8ff"
        self._weather_condition_kind = "cloudy"
        self._weather_summary = "--"
        self._temperature_text = "--C"
        self._humidity_text = "--%"
        self._uv_text = "UV --"

        self._location_name = "Hessigheim"

        self._next_salah_text = "--"
        self._next_salah_name_text = "--"
        self._next_salah_time_only_text = "--:--"
        self._time_left_text = "--H --M"
        self._time_left_progress_value = 0.0
        self._current_salah_text = "--"
        self._current_salah_time_text = "--:--"
        self._hijri_date_text = ""
        self._hijri_month_text = ""
        self._hijri_year_text = ""
        self._current_prayer_breakdown_text = ""
        self._current_prayer_breakdown_items: list[dict] = []
        self._daily_prayer_time_items: list[dict] = []
        self._test_pose_index = self._resolve_test_pose_index()
        self._test_rakat_index = self._resolve_test_rakat_index()
        self._live_pose_index: int | None = None
        self._live_rakat_index: int | None = None
        self._missed_progress_indices: list[int] = []
        self._selected_rakat_index: int | None = None
        self._overlay_prayer_key = ""
        self._rakat_progress_history: dict[int, dict[str, object]] = {}
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
        self._prayer_breakdowns = self._load_prayer_breakdowns()
        self._background_image_url = self._pick_background_url()
        self._background_day = datetime.now().date()
        self._last_adhan_marker = ""
        self._active_adhan_marker = ""
        self._post_adhan_image_url = self._pick_post_adhan_image_url()
        self._post_adhan_visible_until: datetime | None = None
        self._started_at = datetime.now()
        self._test_adhan_after_seconds = self._resolve_test_adhan_after_seconds()
        self._test_adhan_salah = self._resolve_test_adhan_salah()
        self._test_adhan_played = False

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
        self.udp_overlay.close()
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
            self._prayer_alert_marker = ""
            self._dismissed_prayer_alert_marker = ""
            self._auto_closed_prayer_alert_marker = ""
            self._last_adhan_marker = ""
            self._active_adhan_marker = ""
            self.adhan_audio.stop_prayer_reminder()

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

        overlay_state = self.udp_overlay.poll_latest()
        if overlay_state is not None:
            next_pose_index = self._pose_index_from_stage_key(overlay_state.progress_stage_key)
            next_rakat_index = self._rakat_index_from_number(overlay_state.current_rakat)
            overlay_prayer_key = self._normalize_overlay_prayer_key(overlay_state.prayer_name)
            self._update_live_progress_state(next_pose_index, next_rakat_index, overlay_prayer_key)

        prayer = self.prayer.get_status(now)
        self._daily_prayer_time_items = self.prayer.daily_prayer_times(now)
        self._current_salah_text = self._display_salah_name(prayer.current_salah).upper()
        self._current_salah_time_text = self.prayer.salah_time_text(prayer.current_salah, now).upper()
        self._hijri_date_text = self.prayer.hijri_date_text(now)
        self._hijri_month_text = self.prayer.hijri_month_text(now)
        self._hijri_year_text = self.prayer.hijri_year_text(now)
        self._current_prayer_breakdown_text = self._lookup_prayer_breakdown(prayer.current_salah)
        self._current_prayer_breakdown_items = self._lookup_prayer_breakdown_items(prayer.current_salah)
        next_display = self._display_salah_name(prayer.next_salah)
        self._next_salah_text = f"{next_display} {prayer.next_time_text}".upper()
        self._next_salah_name_text = next_display.upper()
        self._next_salah_time_only_text = prayer.next_time_text.upper()
        self._time_left_text = f"{prayer.time_left_text} LEFT".upper()
        self._time_left_progress_value = prayer.time_left_progress
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
            if was_alert_active:
                self._mark_prayer_missed_if_unacknowledged(
                    self._prayer_alert_marker,
                    prayer_name_override=missed_name_override,
                )
            self._prayer_alert_marker = marker
            self._prayer_alert_active = False
        generic_reminder_prayer = prayer.current_salah.strip().lower()
        generic_reminder_active = generic_reminder_prayer in {"fajr", "dhuhr", "asr", "maghrib"}
        should_alert = (
            generic_reminder_active
            and 0 <= prayer.time_left_minutes <= self._prayer_alert_threshold_minutes
        )
        if self._force_prayer_alert:
            should_alert = generic_reminder_active

        if current_is_isha:
            should_alert = self.prayer.isha_reminder_window_active(
                now,
                offset_minutes=30,
                duration_minutes=5,
            )
        should_auto_stop = (
            generic_reminder_active
            and not self._force_prayer_alert
            and 0 <= prayer.time_left_minutes <= 1
        )
        if should_auto_stop:
            self._mark_prayer_missed_if_unacknowledged(self._prayer_alert_marker)
            self._prayer_alert_active = False
        elif current_is_isha:
            self._prayer_alert_active = (
                should_alert
                and self._dismissed_prayer_alert_marker != self._prayer_alert_marker
                and self._auto_closed_prayer_alert_marker != self._prayer_alert_marker
            )
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
        self._play_test_adhan_if_due(now)
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
            return "Dhuhr"
        if key == "maghrib":
            return "Maghrib"
        return salah_name

    def _load_prayer_breakdowns(self) -> dict[str, str]:
        config_path = Path(__file__).resolve().parents[2] / "config" / "prayers.json"
        if not config_path.exists():
            return {}

        try:
            payload = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

        prayers = payload.get("daily_prayers", [])
        if not isinstance(prayers, list):
            return {}

        breakdowns: dict[str, list[dict]] = {}
        for prayer in prayers:
            if not isinstance(prayer, dict):
                continue
            name = prayer.get("name", "")
            breakdown = prayer.get("breakdown", [])
            key = self._normalize_prayer_lookup_key(str(name))
            if not key or not isinstance(breakdown, list):
                continue
            compact_parts: list[dict] = []
            for item in breakdown:
                if not isinstance(item, dict):
                    continue
                part_label = self._compact_breakdown_label(str(item.get("type", "")))
                rakats = item.get("rakats")
                if not part_label or not isinstance(rakats, int):
                    continue
                colors = self._breakdown_colors(part_label)
                compact_parts.append(
                    {
                        "label": f"{part_label}: {rakats}",
                        "accentColor": colors["accentColor"],
                        "borderColor": colors["borderColor"],
                        "fillColor": colors["fillColor"],
                    }
                )
            if compact_parts:
                breakdowns[key] = compact_parts
        return breakdowns

    def _lookup_prayer_breakdown(self, salah_name: str) -> str:
        key = self._normalize_prayer_lookup_key(salah_name)
        items = self._prayer_breakdowns.get(key, [])
        return "  ".join(
            item["label"] for item in items if isinstance(item, dict) and isinstance(item.get("label"), str)
        )

    def _lookup_prayer_breakdown_items(self, salah_name: str) -> list[dict]:
        key = self._normalize_prayer_lookup_key(salah_name)
        items = self._prayer_breakdowns.get(key, [])
        if not isinstance(items, list):
            return []
        return [item for item in items if isinstance(item, dict)]

    def _normalize_prayer_lookup_key(self, salah_name: str) -> str:
        key = salah_name.strip().lower()
        if key == "before fajr":
            return "isha"
        return key

    def _compact_breakdown_label(self, prayer_type: str) -> str:
        normalized = prayer_type.strip().lower().replace(")", "")
        if normalized.startswith("sunnah gm"):
            return "SGM"
        if normalized.startswith("sunnah m"):
            return "SM"
        if normalized == "fard":
            return "F"
        if normalized == "nafl":
            return "N"
        if normalized == "witr":
            return "W"
        return prayer_type.strip().upper()

    def _breakdown_colors(self, label: str) -> dict[str, str]:
        if label == "F":
            return {
                "accentColor": "#ffd978",
                "borderColor": "#d4a53d",
                "fillColor": "#26d4a53d",
            }
        if label in {"SM", "SGM"}:
            return {
                "accentColor": "#7be8ff",
                "borderColor": "#3aa8c6",
                "fillColor": "#203aa8c6",
            }
        if label == "N":
            return {
                "accentColor": "#bff08a",
                "borderColor": "#69b84a",
                "fillColor": "#2069b84a",
            }
        if label == "W":
            return {
                "accentColor": "#ffb6ff",
                "borderColor": "#c274c7",
                "fillColor": "#20c274c7",
            }
        return {
            "accentColor": "#f6fbff",
            "borderColor": "#6a89a3",
            "fillColor": "#1cffffff",
        }

    def _resolve_test_pose_index(self) -> int:
        stage_name = os.getenv("HH_TEST_SALAH_PROGRESS_NAME", "").strip()
        if stage_name:
            normalized = self._normalize_progress_stage_name(stage_name)
            if normalized in self._SALAH_PROGRESS_STAGE_KEYS:
                return self._SALAH_PROGRESS_STAGE_KEYS.index(normalized)

        return max(0, int(os.getenv("HH_TEST_SALAH_PROGRESS_INDEX", "0") or "0"))

    def _resolve_test_rakat_index(self) -> int:
        rakat_number = os.getenv("HH_TEST_RAKAT_NUMBER", "").strip()
        if rakat_number:
            try:
                parsed = int(rakat_number)
                if parsed > 0:
                    return max(0, parsed - 1)
            except ValueError:
                pass

        return max(0, int(os.getenv("HH_TEST_RAKAT_INDEX", "0") or "0"))

    def _pose_index_from_stage_key(self, stage_key: str) -> int | None:
        normalized = self._normalize_progress_stage_name(stage_key)
        if normalized in self._SALAH_PROGRESS_STAGE_KEYS:
            return self._SALAH_PROGRESS_STAGE_KEYS.index(normalized)
        return None

    def _rakat_index_from_number(self, current_rakat: int) -> int:
        return max(0, min(3, current_rakat - 1))

    def _update_live_progress_state(
        self,
        next_pose_index: int | None,
        next_rakat_index: int,
        overlay_prayer_key: str,
    ) -> None:
        if overlay_prayer_key and overlay_prayer_key != self._overlay_prayer_key:
            self._overlay_prayer_key = overlay_prayer_key
            self._rakat_progress_history = {}
            self._selected_rakat_index = None
        elif self._live_rakat_index is not None and next_rakat_index < self._live_rakat_index:
            self._rakat_progress_history = {}
            self._selected_rakat_index = None

        if next_pose_index is None:
            self._live_rakat_index = next_rakat_index
            return

        if (
            self._live_rakat_index is not None
            and next_rakat_index > self._live_rakat_index
        ):
            self._finalize_previous_rakat(self._live_rakat_index)

        rakat_state = self._rakat_progress_history.setdefault(
            next_rakat_index,
            {"pose_index": None, "missed_indices": []},
        )
        previous_pose_index = rakat_state["pose_index"]
        missed_indices = list(rakat_state["missed_indices"])
        if previous_pose_index is None:
            missed_indices = []
        elif next_pose_index < previous_pose_index:
            missed_indices = []
        elif next_pose_index > previous_pose_index + 1:
            skipped = range(previous_pose_index + 1, next_pose_index)
            missed_indices = sorted(set(missed_indices).union(skipped))

        rakat_state["pose_index"] = next_pose_index
        rakat_state["missed_indices"] = missed_indices
        self._live_rakat_index = next_rakat_index
        self._live_pose_index = next_pose_index
        self._missed_progress_indices = missed_indices

    def _finalize_previous_rakat(self, rakat_index: int) -> None:
        rakat_state = self._rakat_progress_history.setdefault(
            rakat_index,
            {"pose_index": None, "missed_indices": []},
        )
        previous_pose_index = rakat_state.get("pose_index")
        if not isinstance(previous_pose_index, int):
            return

        missed_indices = list(rakat_state.get("missed_indices", []))
        final_required_index = self._SALAH_PROGRESS_STAGE_KEYS.index("sajda_2")
        if previous_pose_index < final_required_index:
            trailing_missing = range(previous_pose_index + 1, final_required_index + 1)
            missed_indices = sorted(set(missed_indices).union(trailing_missing))
            rakat_state["missed_indices"] = missed_indices

    def _normalize_overlay_prayer_key(self, prayer_name: str) -> str:
        primary = prayer_name.split("/", 1)[0].strip().lower()
        return primary

    def _normalize_progress_stage_name(self, stage_name: str) -> str:
        normalized = stage_name.strip().lower()
        normalized = normalized.replace("'", "")
        normalized = normalized.replace("-", "")
        normalized = normalized.replace(" ", "")
        aliases = {
            "qiyam": "qiyam",
            "ruku": "ruku",
            "ruku": "ruku",
            "itidal": "itidal",
            "sajda": "sajda_1",
            "sajda1": "sajda_1",
            "jalsa": "jalsa",
            "sajda2": "sajda_2",
            "taslim": "taslim",
        }
        return aliases.get(normalized, normalized)

    def _resolve_test_adhan_after_seconds(self) -> int | None:
        raw = os.getenv("HH_TEST_ADHAN_AFTER_SECONDS", "").strip()
        if not raw:
            return None
        try:
            value = int(raw)
        except ValueError:
            return None
        return value if value >= 0 else None

    def _resolve_test_adhan_salah(self) -> str:
        raw = os.getenv("HH_TEST_ADHAN_SALAH", "").strip()
        return raw if raw else "Fajr"

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
        if prayer_name and prayer_name not in self._missed_prayer_items:
            self._missed_prayer_items.append(prayer_name)
        self._missed_prayer_count = len(self._missed_prayer_items)

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

    def _play_test_adhan_if_due(self, now: datetime) -> None:
        if self._test_adhan_played or self._test_adhan_after_seconds is None:
            return
        if (now - self._started_at).total_seconds() < self._test_adhan_after_seconds:
            return
        salah_name = self._test_adhan_salah
        marker = f"test:{salah_name.lower()}"
        if marker == self._last_adhan_marker:
            self._test_adhan_played = True
            return
        if self.adhan_audio.play_for_salah(salah_name):
            self._last_adhan_marker = marker
            self._active_adhan_marker = marker
            self._test_adhan_played = True

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
    def nextSalahNameText(self) -> str:
        return self._next_salah_name_text

    @Property(str, notify=dataChanged)
    def nextSalahTimeOnlyText(self) -> str:
        return self._next_salah_time_only_text

    @Property(str, notify=dataChanged)
    def timeLeftText(self) -> str:
        return self._time_left_text

    @Property(float, notify=dataChanged)
    def timeLeftProgressValue(self) -> float:
        return float(max(0.0, min(1.0, self._time_left_progress_value)))

    @Property(str, notify=dataChanged)
    def currentSalahText(self) -> str:
        return self._current_salah_text

    @Property(str, notify=dataChanged)
    def currentSalahTimeText(self) -> str:
        return self._current_salah_time_text

    @Property(str, notify=dataChanged)
    def hijriDateText(self) -> str:
        return self._hijri_date_text

    @Property(str, notify=dataChanged)
    def hijriMonthText(self) -> str:
        return self._hijri_month_text

    @Property(str, notify=dataChanged)
    def hijriYearText(self) -> str:
        return self._hijri_year_text

    @Property(str, notify=dataChanged)
    def currentPrayerBreakdownText(self) -> str:
        return self._current_prayer_breakdown_text

    @Property("QVariantList", notify=dataChanged)
    def currentPrayerBreakdownItems(self) -> list[dict]:
        return self._current_prayer_breakdown_items

    @Property("QVariantList", notify=dataChanged)
    def dailyPrayerTimeItems(self) -> list[dict]:
        return self._daily_prayer_time_items

    @Property(int, notify=dataChanged)
    def currentSalahProgressIndex(self) -> int:
        return self._live_pose_index if self._live_pose_index is not None else self._test_pose_index

    @Property(int, notify=dataChanged)
    def currentRakatIndex(self) -> int:
        return self._live_rakat_index if self._live_rakat_index is not None else self._test_rakat_index

    @Property(int, notify=dataChanged)
    def selectedRakatIndex(self) -> int:
        return self._selected_rakat_index if self._selected_rakat_index is not None else self.currentRakatIndex

    @Property(int, notify=dataChanged)
    def displayedSalahProgressIndex(self) -> int:
        state = self._rakat_progress_history.get(self.selectedRakatIndex)
        if state is not None:
            pose_index = state.get("pose_index")
            if isinstance(pose_index, int):
                return pose_index
        return self.currentSalahProgressIndex

    @Property("QVariantList", notify=dataChanged)
    def missedProgressIndices(self) -> list[int]:
        state = self._rakat_progress_history.get(self.selectedRakatIndex)
        if state is not None:
            missed_indices = state.get("missed_indices")
            if isinstance(missed_indices, list):
                return missed_indices
        return self._missed_progress_indices

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

    @Slot(int)
    def selectRakat(self, index: int) -> None:
        if index < 0 or index > 4:
            return
        self._selected_rakat_index = index
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
    _apply_test_screen(window, app)
    window.showFullScreen()
    return app.exec()


def _apply_test_screen(window, app: QGuiApplication) -> None:
    raw_screen = os.getenv("HH_TEST_SCREEN", "").strip()
    if not raw_screen:
        return

    try:
        requested = int(raw_screen)
    except ValueError:
        return

    screens = app.screens()
    if not screens:
        return

    # Human-friendly: 1 means first screen, 4 means fourth screen.
    screen_index = requested - 1 if requested > 0 else 0
    if screen_index < 0 or screen_index >= len(screens):
        return

    screen = screens[screen_index]
    window.setScreen(screen)
    geometry = screen.geometry()
    window.setX(geometry.x())
    window.setY(geometry.y())
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
