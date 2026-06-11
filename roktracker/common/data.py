import datetime
from dataclasses import dataclass, field

from roktracker.utils.general import format_timedelta_to_HHMMSS


@dataclass
class AdditionalScanData:
    current_governor: int = 0
    target_governor: int = 300
    remaining_sec: float = 0.0
    current_time: datetime.datetime = field(default_factory=datetime.datetime.now)

    def eta(self) -> str:
        return format_timedelta_to_HHMMSS(
            datetime.timedelta(seconds=self.remaining_sec)
        )

    def current_time_str(self) -> str:
        return self.current_time.strftime("%H:%M:%S")
