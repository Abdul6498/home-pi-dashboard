from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    weather_api_key: str
    default_lat: float
    default_lon: float
    ui_theme: str


def load_settings() -> Settings:
    return Settings(
        weather_api_key=os.getenv("WEATHER_API_KEY", "").strip(),
        default_lat=float(os.getenv("DEFAULT_LAT", "52.5200")),
        default_lon=float(os.getenv("DEFAULT_LON", "13.4050")),
        ui_theme=os.getenv("UI_THEME", "aurora").strip() or "aurora",
    )
