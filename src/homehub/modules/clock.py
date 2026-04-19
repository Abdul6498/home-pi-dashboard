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
    def update(self) -> ClockSnapshot:
        now = datetime.now()
        return ClockSnapshot(
            time_text=now.strftime("%I:%M"),
            seconds_text=now.strftime("%S"),
            period_text=now.strftime("%p"),
            weekday_text=now.strftime("%a").upper(),
            date_text=now.strftime("%b %d").upper(),
        )
