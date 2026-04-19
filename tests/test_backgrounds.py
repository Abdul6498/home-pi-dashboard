from pathlib import Path

from homehub.ui.backgrounds import prepare_background_asset


def test_prepare_background_asset_returns_none_when_source_missing(tmp_path: Path) -> None:
    result = prepare_background_asset(
        source_path=tmp_path / "missing.jpg",
        cache_dir=tmp_path / "cache",
        width=1024,
        height=600,
    )
    assert result is None
