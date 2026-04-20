from datetime import datetime, timedelta

from homehub.services.prayer_time_service import PrayerTimeService


def test_prayer_service_fallback_status_without_client() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")
    service._client = None  # noqa: SLF001
    status = service.get_status()
    assert status.next_time_text
    assert status.current_salah


def test_due_salah_for_adhan_detects_prayer_start() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Today:
        timings = {
            "Fajr": datetime(2026, 4, 20, 5, 0),
            "Dhuhr": datetime(2026, 4, 20, 13, 15),
            "Asr": datetime(2026, 4, 20, 17, 0),
            "Maghrib": datetime(2026, 4, 20, 20, 20),
            "Isha": datetime(2026, 4, 20, 22, 0),
        }

    class _Tomorrow:
        timings = {
            "Fajr": datetime(2026, 4, 21, 5, 1),
        }

    service._schedule_today = _Today()  # noqa: SLF001
    service._schedule_tomorrow = _Tomorrow()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 20).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 20, 13, 0)  # noqa: SLF001

    due = service.due_salah_for_adhan(datetime(2026, 4, 20, 13, 15, 20))

    assert due == "Dhuhr"


def test_get_status_over_midnight_formats_next_prayer_in_12_hour_time() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Today:
        timings = {
            "Fajr": datetime(2026, 4, 20, 4, 44),
            "Dhuhr": datetime(2026, 4, 20, 13, 15),
            "Asr": datetime(2026, 4, 20, 17, 0),
            "Maghrib": datetime(2026, 4, 20, 20, 20),
            "Isha": datetime(2026, 4, 20, 22, 2),
        }

    class _Tomorrow:
        timings = {
            "Fajr": datetime(2026, 4, 21, 4, 44),
        }

    service._schedule_today = _Today()  # noqa: SLF001
    service._schedule_tomorrow = _Tomorrow()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 20).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 20, 22, 0)  # noqa: SLF001

    status = service.get_status(datetime(2026, 4, 20, 22, 15))

    assert status.current_salah == "Isha"
    assert status.next_salah == "Fajr"
    assert status.next_time_text == "04:44 AM"
    assert status.time_left_text == "06h 29m"


def test_get_status_normalizes_same_day_fajr_to_tomorrow_when_after_isha() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Today:
        timings = {
            "Fajr": datetime(2026, 4, 20, 4, 44),
            "Dhuhr": datetime(2026, 4, 20, 13, 15),
            "Asr": datetime(2026, 4, 20, 17, 0),
            "Maghrib": datetime(2026, 4, 20, 20, 20),
            "Isha": datetime(2026, 4, 20, 22, 2),
        }

    class _TomorrowButWrongDate:
        timings = {
            "Fajr": datetime(2026, 4, 20, 4, 44),
        }

    service._schedule_today = _Today()  # noqa: SLF001
    service._schedule_tomorrow = _TomorrowButWrongDate()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 20).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 20, 22, 0)  # noqa: SLF001

    status = service.get_status(datetime(2026, 4, 20, 22, 22))

    assert status.current_salah == "Isha"
    assert status.next_salah == "Fajr"
    assert status.next_time_text == "04:44 AM"
    assert status.time_left_text == "06h 22m"


def test_get_status_keeps_positive_overnight_countdown_for_isha_to_fajr() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Today:
        timings = {
            "Fajr": datetime(2026, 4, 20, 4, 44),
            "Dhuhr": datetime(2026, 4, 20, 13, 15),
            "Asr": datetime(2026, 4, 20, 17, 0),
            "Maghrib": datetime(2026, 4, 20, 20, 20),
            "Isha": datetime(2026, 4, 20, 22, 2),
        }

    class _Tomorrow:
        timings = {
            "Fajr": datetime(2026, 4, 21, 4, 44),
        }

    service._schedule_today = _Today()  # noqa: SLF001
    service._schedule_tomorrow = _Tomorrow()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 20).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 20, 22, 0)  # noqa: SLF001

    status = service.get_status(datetime(2026, 4, 20, 22, 22))

    assert status.current_salah == "Isha"
    assert status.next_salah == "Fajr"
    assert status.next_time_text == "04:44 AM"
    assert status.time_left_text == "06h 22m"


def test_due_salah_refreshes_stale_schedule_from_live_source() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany", refresh_interval=timedelta(hours=1))
    service._client = object()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 20).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 20, 8, 0)  # noqa: SLF001

    class _StaleToday:
        timings = {
            "Fajr": datetime(2026, 4, 20, 4, 44),
            "Dhuhr": datetime(2026, 4, 20, 13, 10),
            "Asr": datetime(2026, 4, 20, 17, 0),
            "Maghrib": datetime(2026, 4, 20, 20, 20),
            "Isha": datetime(2026, 4, 20, 22, 2),
        }

    class _FreshToday:
        timings = {
            "Fajr": datetime(2026, 4, 20, 4, 44),
            "Dhuhr": datetime(2026, 4, 20, 13, 15),
            "Asr": datetime(2026, 4, 20, 17, 0),
            "Maghrib": datetime(2026, 4, 20, 20, 20),
            "Isha": datetime(2026, 4, 20, 22, 2),
        }

    class _Tomorrow:
        timings = {
            "Fajr": datetime(2026, 4, 21, 4, 44),
        }

    service._schedule_today = _StaleToday()  # noqa: SLF001
    service._schedule_tomorrow = _Tomorrow()  # noqa: SLF001

    def _fake_fetch(target_day):  # noqa: ANN001
        if target_day == datetime(2026, 4, 20).date():
            return _FreshToday()
        return _Tomorrow()

    service._fetch_schedule = _fake_fetch  # type: ignore[method-assign]  # noqa: SLF001

    due = service.due_salah_for_adhan(datetime(2026, 4, 20, 13, 15, 20))

    assert due == "Dhuhr"
