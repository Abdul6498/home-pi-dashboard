from dataclasses import dataclass

from homehub.services.weather_service import WeatherService


@dataclass
class ForecastDaySnapshot:
    day_label: str
    icon: str
    icon_color: str
    low_c: int
    high_c: int


@dataclass
class WeatherSnapshot:
    summary: str
    condition_kind: str
    temperature_c: int
    humidity_pct: int
    uv_index: int
    forecast: list[ForecastDaySnapshot]


class WeatherModule:
    def __init__(self, service: WeatherService):
        self._service = service

    def update(self) -> WeatherSnapshot:
        data = self._service.fetch_current()
        condition_kind, summary, icon, icon_color = self._style_for_code(
            int(data.get("weather_code", 3))
        )
        raw_forecast = data.get("forecast", [])
        forecast: list[ForecastDaySnapshot] = []
        for item in raw_forecast[:5]:
            _, _, card_icon, card_icon_color = self._style_for_code(
                int(item.get("weather_code", 3))
            )
            forecast.append(
                ForecastDaySnapshot(
                    day_label=str(item.get("day_label", "--")),
                    icon=card_icon,
                    icon_color=card_icon_color,
                    low_c=int(item.get("low_c", 0)),
                    high_c=int(item.get("high_c", 0)),
                )
            )

        return WeatherSnapshot(
            summary=summary,
            condition_kind=condition_kind,
            temperature_c=int(data.get("temperature_c", 0)),
            humidity_pct=int(data.get("humidity_pct", 0)),
            uv_index=int(data.get("uv_index", 0)),
            forecast=forecast,
        )

    def _style_for_code(self, weather_code: int) -> tuple[str, str, str, str]:
        if weather_code == 0:
            return ("clear", "Clear", "☀", "#ffd34d")
        if weather_code in {1, 2}:
            return ("partly_cloudy", "Partly Cloudy", "⛅", "#ffd34d")
        if weather_code == 3:
            return ("cloudy", "Cloudy", "☁", "#68c8ff")
        if weather_code in {45, 48}:
            return ("fog", "Fog", "〰", "#9eb3c9")
        if weather_code in {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82}:
            return ("rainy", "Rainy", "☂", "#62c2ff")
        if weather_code in {71, 73, 75, 77, 85, 86}:
            return ("snowy", "Snow", "❄", "#d8ecff")
        if weather_code in {95, 96, 99}:
            return ("storm", "Thunderstorm", "⚡", "#ffd34d")
        return ("cloudy", "Cloudy", "☁", "#68c8ff")
