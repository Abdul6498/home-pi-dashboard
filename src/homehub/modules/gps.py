from dataclasses import dataclass

from homehub.services.gps_service import GPSService


@dataclass
class GPSSnapshot:
    location_name: str
    lat: float
    lon: float


class GPSModule:
    def __init__(self, service: GPSService):
        self._service = service

    def update(self) -> GPSSnapshot:
        data = self._service.fetch_location()
        return GPSSnapshot(
            location_name=data["location_name"],
            lat=data["lat"],
            lon=data["lon"],
        )
