from typing import Any


class WeatherService:
    """Weather provider adapter.

    V1 returns deterministic placeholder data.
    Replace with a real API client in Phase 1 implementation.
    """

    def __init__(self, api_key: str):
        self._api_key = api_key

    def fetch_current(self) -> dict[str, Any]:
        # Placeholder until API integration is added.
        return {
            "summary": "Clear",
            "temperature_c": 21,
        }
