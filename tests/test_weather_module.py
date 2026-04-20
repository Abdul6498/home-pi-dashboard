from homehub.modules.weather import WeatherModule
from homehub.services.weather_service import WeatherService


def test_weather_module_provides_six_forecast_days_from_fallback() -> None:
    module = WeatherModule(WeatherService(api_key=""))
    snapshot = module.update()
    assert len(snapshot.forecast) == 6
    assert snapshot.forecast[-1].day_label == "SAT"
