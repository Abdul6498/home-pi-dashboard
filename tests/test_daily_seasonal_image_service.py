from pathlib import Path

from homehub.services.daily_seasonal_image_service import DailySeasonalImageService


def test_find_existing_daily_image_in_cache(tmp_path: Path) -> None:
    service = DailySeasonalImageService(cache_dir=tmp_path)
    existing = tmp_path / "spring_2026-04-19.jpg"
    existing.write_bytes(b"fake")
    found = service._find_existing("spring_2026-04-19")  # noqa: SLF001
    assert found == existing
