from homehub.services.prayer_time_service import PrayerTimeService


def test_prayer_service_fallback_status_without_client() -> None:
    service = PrayerTimeService(city="Hessigheim", country="Germany")
    service._client = None  # noqa: SLF001
    status = service.get_status()
    assert status.next_time_text
    assert status.current_salah
