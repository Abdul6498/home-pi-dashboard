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

    class _Yesterday:
        timings = {
            "Isha": datetime(2026, 4, 19, 22, 0),
        }

    class _Today:
        timings = {
            "Imsak": datetime(2026, 4, 20, 4, 50),
            "Fajr": datetime(2026, 4, 20, 5, 0),
            "Sunrise": datetime(2026, 4, 20, 6, 25),
            "Dhuhr": datetime(2026, 4, 20, 13, 15),
            "Asr": datetime(2026, 4, 20, 17, 0),
            "Maghrib": datetime(2026, 4, 20, 20, 20),
            "Isha": datetime(2026, 4, 20, 22, 0),
        }

    class _Tomorrow:
        timings = {
            "Imsak": datetime(2026, 4, 21, 4, 49),
            "Fajr": datetime(2026, 4, 21, 5, 1),
        }

    service._schedule_yesterday = _Yesterday()  # noqa: SLF001
    service._schedule_today = _Today()  # noqa: SLF001
    service._schedule_tomorrow = _Tomorrow()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 20).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 20, 13, 0)  # noqa: SLF001

    due = service.due_salah_for_adhan(datetime(2026, 4, 20, 13, 15, 20))

    assert due == "Dhuhr"


def test_due_salah_for_adhan_triggers_fajr_thirty_minutes_before_sunrise() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Yesterday:
        timings = {
            "Isha": datetime(2026, 4, 19, 22, 0),
        }

    class _Today:
        timings = {
            "Imsak": datetime(2026, 4, 20, 4, 50),
            "Fajr": datetime(2026, 4, 20, 5, 0),
            "Sunrise": datetime(2026, 4, 20, 6, 25),
            "Dhuhr": datetime(2026, 4, 20, 13, 15),
            "Asr": datetime(2026, 4, 20, 17, 0),
            "Maghrib": datetime(2026, 4, 20, 20, 20),
            "Isha": datetime(2026, 4, 20, 22, 0),
        }

    class _Tomorrow:
        timings = {
            "Imsak": datetime(2026, 4, 21, 4, 49),
            "Fajr": datetime(2026, 4, 21, 5, 1),
        }

    service._schedule_yesterday = _Yesterday()  # noqa: SLF001
    service._schedule_today = _Today()  # noqa: SLF001
    service._schedule_tomorrow = _Tomorrow()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 20).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 20, 5, 50)  # noqa: SLF001

    due = service.due_salah_for_adhan(datetime(2026, 4, 20, 5, 55, 20))

    assert due == "Fajr"


def test_get_status_over_midnight_formats_next_prayer_in_12_hour_time() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Yesterday:
        timings = {
            "Isha": datetime(2026, 4, 19, 22, 1),
        }

    class _Today:
        timings = {
            "Imsak": datetime(2026, 4, 20, 4, 33),
            "Fajr": datetime(2026, 4, 20, 4, 44),
            "Sunrise": datetime(2026, 4, 20, 6, 18),
            "Dhuhr": datetime(2026, 4, 20, 13, 15),
            "Asr": datetime(2026, 4, 20, 17, 0),
            "Maghrib": datetime(2026, 4, 20, 20, 20),
            "Isha": datetime(2026, 4, 20, 22, 2),
        }

    class _Tomorrow:
        timings = {
            "Imsak": datetime(2026, 4, 21, 4, 44),
            "Fajr": datetime(2026, 4, 21, 4, 44),
        }

    service._schedule_yesterday = _Yesterday()  # noqa: SLF001
    service._schedule_today = _Today()  # noqa: SLF001
    service._schedule_tomorrow = _Tomorrow()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 20).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 20, 22, 0)  # noqa: SLF001

    status = service.get_status(datetime(2026, 4, 20, 22, 15))

    assert status.current_salah == "Isha"
    assert status.next_salah == "Imsak"
    assert status.next_time_text == "04:44 AM"
    assert status.time_left_text == "06h 29m"


def test_get_status_normalizes_same_day_fajr_to_tomorrow_when_after_isha() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Yesterday:
        timings = {
            "Isha": datetime(2026, 4, 19, 22, 1),
        }

    class _Today:
        timings = {
            "Imsak": datetime(2026, 4, 20, 4, 33),
            "Fajr": datetime(2026, 4, 20, 4, 44),
            "Sunrise": datetime(2026, 4, 20, 6, 18),
            "Dhuhr": datetime(2026, 4, 20, 13, 15),
            "Asr": datetime(2026, 4, 20, 17, 0),
            "Maghrib": datetime(2026, 4, 20, 20, 20),
            "Isha": datetime(2026, 4, 20, 22, 2),
        }

    class _TomorrowButWrongDate:
        timings = {
            "Imsak": datetime(2026, 4, 21, 4, 44),
            "Fajr": datetime(2026, 4, 20, 4, 44),
        }

    service._schedule_yesterday = _Yesterday()  # noqa: SLF001
    service._schedule_today = _Today()  # noqa: SLF001
    service._schedule_tomorrow = _TomorrowButWrongDate()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 20).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 20, 22, 0)  # noqa: SLF001

    status = service.get_status(datetime(2026, 4, 20, 22, 22))

    assert status.current_salah == "Isha"
    assert status.next_salah == "Imsak"
    assert status.next_time_text == "04:44 AM"
    assert status.time_left_text == "06h 22m"


def test_get_status_keeps_positive_overnight_countdown_for_isha_to_fajr() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Yesterday:
        timings = {
            "Isha": datetime(2026, 4, 19, 22, 1),
        }

    class _Today:
        timings = {
            "Imsak": datetime(2026, 4, 20, 4, 33),
            "Fajr": datetime(2026, 4, 20, 4, 44),
            "Sunrise": datetime(2026, 4, 20, 6, 18),
            "Dhuhr": datetime(2026, 4, 20, 13, 15),
            "Asr": datetime(2026, 4, 20, 17, 0),
            "Maghrib": datetime(2026, 4, 20, 20, 20),
            "Isha": datetime(2026, 4, 20, 22, 2),
        }

    class _Tomorrow:
        timings = {
            "Imsak": datetime(2026, 4, 21, 4, 44),
            "Fajr": datetime(2026, 4, 21, 4, 44),
        }

    service._schedule_yesterday = _Yesterday()  # noqa: SLF001
    service._schedule_today = _Today()  # noqa: SLF001
    service._schedule_tomorrow = _Tomorrow()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 20).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 20, 22, 0)  # noqa: SLF001

    status = service.get_status(datetime(2026, 4, 20, 22, 22))

    assert status.current_salah == "Isha"
    assert status.next_salah == "Imsak"
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


def test_get_status_uses_fajr_window_until_sunrise() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Yesterday:
        timings = {
            "Isha": datetime(2026, 4, 21, 22, 6),
        }

    class _Today:
        timings = {
            "Imsak": datetime(2026, 4, 22, 4, 29),
            "Fajr": datetime(2026, 4, 22, 4, 39),
            "Sunrise": datetime(2026, 4, 22, 6, 19),
            "Dhuhr": datetime(2026, 4, 22, 13, 22),
            "Asr": datetime(2026, 4, 22, 18, 16),
            "Maghrib": datetime(2026, 4, 22, 20, 26),
            "Isha": datetime(2026, 4, 22, 22, 6),
        }

    class _Tomorrow:
        timings = {
            "Imsak": datetime(2026, 4, 23, 4, 28),
            "Fajr": datetime(2026, 4, 23, 4, 38),
        }

    service._schedule_yesterday = _Yesterday()  # noqa: SLF001
    service._schedule_today = _Today()  # noqa: SLF001
    service._schedule_tomorrow = _Tomorrow()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 22).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 22, 5, 0)  # noqa: SLF001

    status = service.get_status(datetime(2026, 4, 22, 5, 0))

    assert status.current_salah == "Fajr"
    assert status.next_salah == "Dhuhr"
    assert status.next_time_text == "01:22 PM"
    assert status.time_left_text == "01h 19m"


def test_get_status_after_sunrise_switches_to_before_dhuhr() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Yesterday:
        timings = {
            "Isha": datetime(2026, 4, 21, 22, 6),
        }

    class _Today:
        timings = {
            "Imsak": datetime(2026, 4, 22, 4, 29),
            "Fajr": datetime(2026, 4, 22, 4, 39),
            "Sunrise": datetime(2026, 4, 22, 6, 19),
            "Dhuhr": datetime(2026, 4, 22, 13, 22),
            "Asr": datetime(2026, 4, 22, 18, 16),
            "Maghrib": datetime(2026, 4, 22, 20, 26),
            "Isha": datetime(2026, 4, 22, 22, 6),
        }

    class _Tomorrow:
        timings = {
            "Imsak": datetime(2026, 4, 23, 4, 28),
            "Fajr": datetime(2026, 4, 23, 4, 38),
        }

    service._schedule_yesterday = _Yesterday()  # noqa: SLF001
    service._schedule_today = _Today()  # noqa: SLF001
    service._schedule_tomorrow = _Tomorrow()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 22).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 22, 7, 0)  # noqa: SLF001

    status = service.get_status(datetime(2026, 4, 22, 7, 0))

    assert status.current_salah == "Before Dhuhr"
    assert status.next_salah == "Dhuhr"
    assert status.next_time_text == "01:22 PM"
    assert status.time_left_text == "06h 22m"


def test_get_status_uses_isha_window_until_next_imsak() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Yesterday:
        timings = {
            "Isha": datetime(2026, 4, 21, 22, 6),
        }

    class _Today:
        timings = {
            "Imsak": datetime(2026, 4, 22, 4, 29),
            "Fajr": datetime(2026, 4, 22, 4, 39),
            "Sunrise": datetime(2026, 4, 22, 6, 19),
            "Dhuhr": datetime(2026, 4, 22, 13, 22),
            "Asr": datetime(2026, 4, 22, 18, 16),
            "Maghrib": datetime(2026, 4, 22, 20, 26),
            "Isha": datetime(2026, 4, 22, 22, 6),
        }

    class _Tomorrow:
        timings = {
            "Imsak": datetime(2026, 4, 23, 4, 28),
            "Fajr": datetime(2026, 4, 23, 4, 38),
        }

    service._schedule_yesterday = _Yesterday()  # noqa: SLF001
    service._schedule_today = _Today()  # noqa: SLF001
    service._schedule_tomorrow = _Tomorrow()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 22).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 22, 22, 30)  # noqa: SLF001

    status = service.get_status(datetime(2026, 4, 22, 23, 0))

    assert status.current_salah == "Isha"
    assert status.next_salah == "Imsak"
    assert status.next_time_text == "04:28 AM"
    assert status.time_left_text == "05h 28m"


def test_get_status_keeps_isha_until_imsak_after_midnight() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Yesterday:
        timings = {
            "Isha": datetime(2026, 4, 22, 22, 6),
        }

    class _Today:
        timings = {
            "Imsak": datetime(2026, 4, 23, 4, 28),
            "Fajr": datetime(2026, 4, 23, 4, 38),
            "Sunrise": datetime(2026, 4, 23, 6, 18),
            "Dhuhr": datetime(2026, 4, 23, 13, 22),
            "Asr": datetime(2026, 4, 23, 18, 16),
            "Maghrib": datetime(2026, 4, 23, 20, 27),
            "Isha": datetime(2026, 4, 23, 22, 7),
        }

    class _Tomorrow:
        timings = {
            "Imsak": datetime(2026, 4, 24, 4, 27),
            "Fajr": datetime(2026, 4, 24, 4, 37),
        }

    service._schedule_yesterday = _Yesterday()  # noqa: SLF001
    service._schedule_today = _Today()  # noqa: SLF001
    service._schedule_tomorrow = _Tomorrow()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 23).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 23, 1, 0)  # noqa: SLF001

    status = service.get_status(datetime(2026, 4, 23, 1, 0))

    assert status.current_salah == "Isha"
    assert status.next_salah == "Imsak"
    assert status.next_time_text == "04:27 AM"
    assert status.time_left_text == "03h 28m"


def test_get_status_uses_maghrib_window_with_next_isha() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Yesterday:
        timings = {
            "Isha": datetime(2026, 4, 21, 22, 6),
        }

    class _Today:
        timings = {
            "Imsak": datetime(2026, 4, 22, 4, 29),
            "Fajr": datetime(2026, 4, 22, 4, 39),
            "Sunrise": datetime(2026, 4, 22, 6, 19),
            "Dhuhr": datetime(2026, 4, 22, 13, 22),
            "Asr": datetime(2026, 4, 22, 18, 16),
            "Maghrib": datetime(2026, 4, 22, 20, 26),
            "Isha": datetime(2026, 4, 22, 22, 6),
        }

    class _Tomorrow:
        timings = {
            "Imsak": datetime(2026, 4, 23, 4, 28),
            "Fajr": datetime(2026, 4, 23, 4, 38),
        }

    service._schedule_yesterday = _Yesterday()  # noqa: SLF001
    service._schedule_today = _Today()  # noqa: SLF001
    service._schedule_tomorrow = _Tomorrow()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 22).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 22, 20, 33)  # noqa: SLF001

    status = service.get_status(datetime(2026, 4, 22, 20, 33))

    assert status.current_salah == "Maghrib"
    assert status.next_salah == "Isha"
    assert status.next_time_text == "10:06 PM"
    assert status.time_left_text == "01h 33m"

def test_get_status_keeps_isha_overnight_when_imsak_is_missing() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Yesterday:
        timings = {
            "Isha": datetime(2026, 4, 21, 22, 6),
        }

    class _TodayMissingImsak:
        timings = {
            "Fajr": datetime(2026, 4, 22, 4, 39),
            "Sunrise": datetime(2026, 4, 22, 6, 19),
            "Dhuhr": datetime(2026, 4, 22, 13, 22),
            "Asr": datetime(2026, 4, 22, 18, 16),
            "Maghrib": datetime(2026, 4, 22, 20, 26),
            "Isha": datetime(2026, 4, 22, 22, 6),
        }

    class _TomorrowMissingImsak:
        timings = {
            "Fajr": datetime(2026, 4, 23, 4, 38),
        }

    service._schedule_yesterday = _Yesterday()  # noqa: SLF001
    service._schedule_today = _TodayMissingImsak()  # noqa: SLF001
    service._schedule_tomorrow = _TomorrowMissingImsak()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 22).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 22, 23, 30)  # noqa: SLF001

    status = service.get_status(datetime(2026, 4, 22, 23, 20))

    assert status.current_salah == "Isha"
    assert status.next_salah == "Fajr"

def test_fallback_shows_isha_until_next_fajr_imsak_when_isha_time_missing() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Yesterday:
        timings = {
            "Isha": datetime(2026, 4, 21, 22, 6),
        }

    class _TodayMissingIsha:
        timings = {
            "Imsak": datetime(2026, 4, 22, 4, 29),
            "Fajr": datetime(2026, 4, 22, 4, 39),
            "Sunrise": datetime(2026, 4, 22, 6, 19),
            "Dhuhr": datetime(2026, 4, 22, 13, 22),
            "Asr": datetime(2026, 4, 22, 18, 16),
            "Maghrib": datetime(2026, 4, 22, 20, 26),
        }

    class _Tomorrow:
        timings = {
            "Imsak": datetime(2026, 4, 23, 4, 28),
            "Fajr": datetime(2026, 4, 23, 4, 38),
        }

    service._schedule_yesterday = _Yesterday()  # noqa: SLF001
    service._schedule_today = _TodayMissingIsha()  # noqa: SLF001
    service._schedule_tomorrow = _Tomorrow()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 22).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 22, 22, 30)  # noqa: SLF001

    status = service.get_status(datetime(2026, 4, 22, 22, 30))

    assert status.current_salah == "Isha"
    assert status.next_salah == "Imsak"


def test_fallback_switches_to_before_fajr_after_imsak_before_fajr() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Yesterday:
        timings = {
            "Isha": datetime(2026, 4, 21, 22, 6),
        }

    class _TodayMissingIsha:
        timings = {
            "Imsak": datetime(2026, 4, 22, 4, 29),
            "Fajr": datetime(2026, 4, 22, 4, 39),
            "Sunrise": datetime(2026, 4, 22, 6, 19),
            "Dhuhr": datetime(2026, 4, 22, 13, 22),
            "Asr": datetime(2026, 4, 22, 18, 16),
            "Maghrib": datetime(2026, 4, 22, 20, 26),
        }

    class _Tomorrow:
        timings = {
            "Imsak": datetime(2026, 4, 23, 4, 28),
            "Fajr": datetime(2026, 4, 23, 4, 38),
        }

    service._schedule_yesterday = _Yesterday()  # noqa: SLF001
    service._schedule_today = _TodayMissingIsha()  # noqa: SLF001
    service._schedule_tomorrow = _Tomorrow()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 22).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 22, 4, 31)  # noqa: SLF001

    status = service.get_status(datetime(2026, 4, 22, 4, 31))

    assert status.current_salah == "Imsak"
    assert status.next_salah == "Fajr"


def test_fallback_keeps_isha_when_next_fajr_has_wrong_same_day_date() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Yesterday:
        timings = {
            "Isha": datetime(2026, 4, 21, 22, 6),
        }

    class _Today:
        timings = {
            "Imsak": datetime(2026, 4, 22, 4, 29),
            "Fajr": datetime(2026, 4, 22, 4, 39),
            "Sunrise": datetime(2026, 4, 22, 6, 19),
            "Dhuhr": datetime(2026, 4, 22, 13, 22),
            "Asr": datetime(2026, 4, 22, 18, 16),
            "Maghrib": datetime(2026, 4, 22, 20, 26),
            "Isha": datetime(2026, 4, 22, 22, 6),
        }

    class _TomorrowButWrongDate:
        timings = {
            "Imsak": datetime(2026, 4, 23, 4, 28),
            "Fajr": datetime(2026, 4, 22, 4, 39),
        }

    service._schedule_yesterday = _Yesterday()  # noqa: SLF001
    service._schedule_today = _Today()  # noqa: SLF001
    service._schedule_tomorrow = _TomorrowButWrongDate()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 22).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 22, 22, 30)  # noqa: SLF001

    status = service.get_status(datetime(2026, 4, 22, 22, 37))

    assert status.current_salah == "Isha"
    assert status.next_salah == "Imsak"


def test_isha_reminder_reached_during_fallback_overnight_isha() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Yesterday:
        timings = {
            "Isha": datetime(2026, 4, 21, 22, 6),
        }

    class _Today:
        timings = {
            "Imsak": datetime(2026, 4, 22, 4, 29),
            "Fajr": datetime(2026, 4, 22, 4, 39),
            "Sunrise": datetime(2026, 4, 22, 6, 19),
            "Dhuhr": datetime(2026, 4, 22, 13, 22),
            "Asr": datetime(2026, 4, 22, 18, 16),
            "Maghrib": datetime(2026, 4, 22, 20, 26),
            "Isha": datetime(2026, 4, 22, 22, 6),
        }

    class _TomorrowButWrongDate:
        timings = {
            "Imsak": datetime(2026, 4, 23, 4, 28),
            "Fajr": datetime(2026, 4, 22, 4, 39),
        }

    service._schedule_yesterday = _Yesterday()  # noqa: SLF001
    service._schedule_today = _Today()  # noqa: SLF001
    service._schedule_tomorrow = _TomorrowButWrongDate()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 22).date()  # noqa: SLF001
    service._last_refresh_at = datetime(2026, 4, 22, 22, 30)  # noqa: SLF001

    assert service.isha_reminder_reached(datetime(2026, 4, 22, 22, 35), offset_minutes=30) is False
    assert service.isha_reminder_reached(datetime(2026, 4, 22, 22, 36), offset_minutes=30) is True
