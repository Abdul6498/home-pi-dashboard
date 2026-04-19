from dataclasses import dataclass

from homehub.services.weather_service import WeatherService


@dataclass
class WeatherSnapshot:
    summary: str
    temperature_c: str


class WeatherModule:
    def __init__(self, service: WeatherService):
        self._service = service

    def update(self) -> WeatherSnapshot:
        data = self._service.fetch_current()
        return WeatherSnapshot(
            summary=data.get("summary", "Weather unavailable"),
            temperature_c=str(data.get("temperature_c", "--")),
        )
