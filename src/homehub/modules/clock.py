from dataclasses import dataclass
from datetime import datetime


@dataclass
class ClockSnapshot:
    time_text: str
    seconds_text: str
    period_text: str
    weekday_text: str
    date_text: str


class ClockModule:
    def __init__(self, use_24_hour: bool = False) -> None:
        self._use_24_hour = use_24_hour

    def set_use_24_hour(self, enabled: bool) -> None:
        self._use_24_hour = enabled

    def update(self) -> ClockSnapshot:
        now = datetime.now()
        time_pattern = "%H:%M" if self._use_24_hour else "%I:%M"
        period_text = "" if self._use_24_hour else now.strftime("%p")
        return ClockSnapshot(
            time_text=now.strftime(time_pattern),
            seconds_text=now.strftime("%S"),
            period_text=period_text,
            weekday_text=now.strftime("%a").upper(),
            date_text=now.strftime("%b %d").upper(),
        )
