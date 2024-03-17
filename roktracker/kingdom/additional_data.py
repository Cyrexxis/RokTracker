import datetime

from dataclasses import dataclass

from roktracker.utils.general import format_timedelta_to_HHMMSS


@dataclass
class AdditionalData:
    current_governor: int
    target_governor: int
    skipped_governors: int
    power_ok: str
    kills_ok: str
    reconstruction_success: str
    remaining_sec: float
    current_time: str = datetime.datetime.now().strftime("%H:%M:%S")

    def eta(self) -> str:
        return format_timedelta_to_HHMMSS(
            datetime.timedelta(seconds=self.remaining_sec)
        )
