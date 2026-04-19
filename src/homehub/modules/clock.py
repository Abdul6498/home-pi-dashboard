from dataclasses import dataclass
from datetime import datetime


@dataclass
class ClockSnapshot:
    time_text: str
    date_text: str


class ClockModule:
    def update(self) -> ClockSnapshot:
        now = datetime.now()
        return ClockSnapshot(
            time_text=now.strftime("%H:%M:%S"),
            date_text=now.strftime("%A, %d %B %Y"),
        )
