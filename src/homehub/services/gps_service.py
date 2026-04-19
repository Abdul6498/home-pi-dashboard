class GPSService:
    """GPS provider adapter.

    V1 returns configured fallback coordinates.
    Replace with real serial/NMEA GPS parsing in Phase 1 implementation.
    """

    def __init__(self, fallback_lat: float, fallback_lon: float):
        self._fallback_lat = fallback_lat
        self._fallback_lon = fallback_lon

    def fetch_location(self) -> dict[str, float | str]:
        return {
            "location_name": "Hessigheim",
            "lat": self._fallback_lat,
            "lon": self._fallback_lon,
        }
