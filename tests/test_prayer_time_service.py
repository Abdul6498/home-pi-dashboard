from datetime import datetime

from homehub.services.prayer_time_service import PrayerTimeService


def test_prayer_service_fallback_status_without_client() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")
    service._client = None  # noqa: SLF001
    status = service.get_status()
    assert status.next_time_text
    assert status.current_salah


def test_due_salah_for_adhan_detects_prayer_start() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")

    class _Schedule:
        timings = {
            "Fajr": datetime(2026, 4, 20, 5, 0),
            "Dhuhr": datetime(2026, 4, 20, 13, 15),
            "Asr": datetime(2026, 4, 20, 17, 0),
            "Maghrib": datetime(2026, 4, 20, 20, 20),
            "Isha": datetime(2026, 4, 20, 22, 0),
        }

    service._schedule_today = _Schedule()  # noqa: SLF001
    service._loaded_for_date = datetime(2026, 4, 20).date()  # noqa: SLF001

    due = service.due_salah_for_adhan(datetime(2026, 4, 20, 13, 15, 20))

    assert due == "Dhuhr"
