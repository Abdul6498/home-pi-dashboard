from __future__ import annotations

from datetime import datetime
import json
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen


class WeatherService:
    """Weather provider adapter backed by Open-Meteo."""

    def __init__(self, api_key: str):
        self._api_key = api_key

    def fetch_current(self) -> dict[str, Any]:
        lat = 48.99407
        lon = 9.18629
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code",
            "daily": "temperature_2m_max,temperature_2m_min,weather_code,uv_index_max",
            "timezone": "Europe/Berlin",
            "forecast_days": 7,
        }
        url = f"https://api.open-meteo.com/v1/forecast?{urlencode(params)}"

        try:
            with urlopen(url, timeout=6) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError, OSError, json.JSONDecodeError):
            return self._fallback_payload()

        current = payload.get("current", {})
        daily = payload.get("daily", {})
        days = daily.get("time", [])
        highs = daily.get("temperature_2m_max", [])
        lows = daily.get("temperature_2m_min", [])
        codes = daily.get("weather_code", [])

        forecast: list[dict[str, int | str]] = []
        for idx in range(1, min(7, len(days))):
            day_label = self._format_day_label(str(days[idx]))
            forecast.append(
                {
                    "day_label": day_label,
                    "weather_code": int(codes[idx]) if idx < len(codes) else 3,
                    "low_c": int(round(lows[idx])) if idx < len(lows) else 0,
                    "high_c": int(round(highs[idx])) if idx < len(highs) else 0,
                }
            )

        uv_values = daily.get("uv_index_max", [])
        return {
            "temperature_c": int(round(float(current.get("temperature_2m", 0)))),
            "humidity_pct": int(round(float(current.get("relative_humidity_2m", 0)))),
            "weather_code": int(current.get("weather_code", 3)),
            "uv_index": int(round(float(uv_values[0]))) if uv_values else 0,
            "forecast": forecast,
        }

    def _format_day_label(self, date_iso: str) -> str:
        try:
            return datetime.fromisoformat(date_iso).strftime("%a").upper()
        except ValueError:
            return "--"

    def _fallback_payload(self) -> dict[str, Any]:
        return {
            "temperature_c": 14,
            "humidity_pct": 55,
            "weather_code": 2,
            "uv_index": 3,
            "forecast": [
                {"day_label": "MON", "weather_code": 3, "low_c": 7, "high_c": 14},
                {"day_label": "TUE", "weather_code": 61, "low_c": 6, "high_c": 12},
                {"day_label": "WED", "weather_code": 1, "low_c": 5, "high_c": 15},
                {"day_label": "THU", "weather_code": 2, "low_c": 6, "high_c": 16},
                {"day_label": "FRI", "weather_code": 0, "low_c": 8, "high_c": 19},
                {"day_label": "SAT", "weather_code": 1, "low_c": 9, "high_c": 18},
            ],
        }
