from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

from homehub.services.aladhan_client import AzanTimeService


@dataclass(frozen=True)
class PrayerStatus:
    current_salah: str
    next_salah: str
    next_time_text: str
    time_left_text: str


class PrayerTimeService:
    """Prayer status service backed by the bundled Aladhan client."""

    _SALAH_KEYS = ("Fajr", "Dhuhr", "Asr", "Maghrib", "Isha")

    def __init__(
        self,
        *,
        city: str = "Hessigheim",
        country: str = "Germany",
        latitude: float | None = None,
        longitude: float | None = None,
        refresh_interval: timedelta = timedelta(hours=6),
    ) -> None:
        self._city = city
        self._country = country
        self._latitude = latitude
        self._longitude = longitude
        self._client: Any | None = self._load_azan_service()
        self._schedule_today: Any | None = None
        self._schedule_tomorrow: Any | None = None
        self._loaded_for_date: date | None = None
        self._last_refresh_at: datetime | None = None
        self._refresh_interval = refresh_interval

    def get_status(self, now: datetime | None = None) -> PrayerStatus:
        current_time = now or datetime.now()
        if self._client is None:
            return PrayerStatus(
                current_salah="Salah unknown",
                next_salah="N/A",
                next_time_text="--:--",
                time_left_text="--h --m",
            )

        self._ensure_schedules(current_time)
        if self._schedule_today is None:
            return PrayerStatus(
                current_salah="Salah unavailable",
                next_salah="N/A",
                next_time_text="--:--",
                time_left_text="--h --m",
            )

        timings = self._schedule_today.timings
        tz_now = current_time
        first_timing = next(iter(timings.values()), None)
        if first_timing is not None and first_timing.tzinfo is not None and tz_now.tzinfo is None:
            tz_now = current_time.replace(tzinfo=first_timing.tzinfo)

        current_salah = self._current_salah_name(tz_now, timings)
        next_name, next_moment = self._next_salah(tz_now)

        if next_name is None or next_moment is None:
            return PrayerStatus(
                current_salah=current_salah,
                next_salah="N/A",
                next_time_text="--:--",
                time_left_text="--h --m",
            )

        next_moment = self._resolve_future_next_moment(
            next_name=next_name,
            next_moment=next_moment,
            reference=tz_now,
            current_salah=current_salah,
        )
        delta = next_moment - tz_now
        if delta.total_seconds() < 0:
            delta = timedelta(seconds=0)

        return PrayerStatus(
            current_salah=current_salah,
            next_salah=next_name,
            next_time_text=next_moment.strftime("%I:%M %p"),
            time_left_text=self._format_duration(delta),
        )

    def due_salah_for_adhan(
        self, now: datetime | None = None, *, grace_seconds: int = 120
    ) -> str | None:
        current_time = now or datetime.now()
        if self._client is None:
            return None

        self._ensure_schedules(current_time)
        if self._schedule_today is None:
            return None

        timings = self._schedule_today.timings
        tz_now = current_time
        first_timing = next(iter(timings.values()), None)
        if first_timing is not None and first_timing.tzinfo is not None and tz_now.tzinfo is None:
            tz_now = current_time.replace(tzinfo=first_timing.tzinfo)

        for key in self._SALAH_KEYS:
            moment = timings.get(key)
            if not moment:
                continue
            delta = (tz_now - moment).total_seconds()
            if 0 <= delta <= grace_seconds:
                return key
        return None

    def _ensure_schedules(self, current_time: datetime) -> None:
        today = current_time.date()
        if (
            self._loaded_for_date == today
            and self._schedule_today is not None
            and self._schedule_tomorrow is not None
            and not self._refresh_overdue(current_time)
        ):
            return

        try:
            self._schedule_today = self._fetch_schedule(today)
            self._schedule_tomorrow = self._fetch_schedule(today + timedelta(days=1))
            self._loaded_for_date = today
            self._last_refresh_at = current_time
        except Exception:
            self._schedule_today = None
            self._schedule_tomorrow = None
            self._loaded_for_date = None
            self._last_refresh_at = None

    def _fetch_schedule(self, target_day: date) -> Any:
        if self._client is None:
            raise RuntimeError("Prayer client unavailable")

        try:
            return self._client.daily_prayer_schedule(
                city=self._city,
                country=self._country,
                target_date=target_day,
            )
        except Exception:
            if self._latitude is not None and self._longitude is not None:
                return self._client.daily_prayer_schedule_by_coordinates(
                    latitude=self._latitude,
                    longitude=self._longitude,
                    target_date=target_day,
                )
            raise

    def _next_salah(self, now: datetime) -> tuple[str | None, datetime | None]:
        today = self._schedule_today.timings if self._schedule_today else {}
        for key in self._SALAH_KEYS:
            moment = today.get(key)
            if moment and moment > now:
                return key, moment

        tomorrow = self._schedule_tomorrow.timings if self._schedule_tomorrow else {}
        fajr = tomorrow.get("Fajr")
        if fajr:
            return "Fajr", fajr
        return None, None

    def _normalize_future_moment(self, moment: datetime, reference: datetime) -> datetime:
        adjusted = moment
        while adjusted <= reference:
            adjusted += timedelta(days=1)
        return adjusted

    def _resolve_future_next_moment(
        self,
        *,
        next_name: str,
        next_moment: datetime,
        reference: datetime,
        current_salah: str,
    ) -> datetime:
        adjusted = self._normalize_future_moment(next_moment, reference)

        # Be explicit about the overnight Isha -> Fajr rollover. Some live
        # schedules can arrive with the correct Fajr clock time but an
        # incorrect same-day date, which would otherwise collapse the
        # countdown to zero after clamping.
        if (
            current_salah == "Isha"
            and next_name == "Fajr"
            and adjusted <= reference
        ):
            adjusted = self._combine_with_reference_day(
                reference=reference + timedelta(days=1),
                moment=next_moment,
            )

        if (
            current_salah == "Isha"
            and next_name == "Fajr"
            and adjusted - reference < timedelta(minutes=1)
        ):
            adjusted = self._combine_with_reference_day(
                reference=reference + timedelta(days=1),
                moment=next_moment,
            )

        return self._normalize_future_moment(adjusted, reference)

    def _combine_with_reference_day(self, *, reference: datetime, moment: datetime) -> datetime:
        combined = datetime.combine(reference.date(), moment.timetz())
        if reference.tzinfo is not None and combined.tzinfo is None:
            combined = combined.replace(tzinfo=reference.tzinfo)
        return combined

    def _current_salah_name(self, now: datetime, timings: dict[str, datetime]) -> str:
        current = "Before Fajr"
        for key in self._SALAH_KEYS:
            moment = timings.get(key)
            if moment and moment <= now:
                current = key
        return current

    def _refresh_overdue(self, current_time: datetime) -> bool:
        if self._last_refresh_at is None:
            return True
        reference = self._last_refresh_at
        if reference.tzinfo is not None and current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=reference.tzinfo)
        elif reference.tzinfo is None and current_time.tzinfo is not None:
            reference = reference.replace(tzinfo=current_time.tzinfo)
        return current_time - reference >= self._refresh_interval

    def _load_azan_service(self) -> Any | None:
        try:
            return AzanTimeService()
        except Exception:
            return None

    def _format_duration(self, delta: timedelta) -> str:
        minutes_total = int(delta.total_seconds() // 60)
        hours = minutes_total // 60
        minutes = minutes_total % 60
        return f"{hours:02d}h {minutes:02d}m"
