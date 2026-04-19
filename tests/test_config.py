from homehub.config import load_settings


def test_load_settings_defaults() -> None:
    settings = load_settings()
    assert settings.ui_theme
