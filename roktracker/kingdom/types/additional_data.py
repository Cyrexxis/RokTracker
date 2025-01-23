import datetime

from pydantic import BaseModel

from roktracker.utils.general import format_timedelta_to_HHMMSS


class AdditionalData(BaseModel):
    current_governor: int
    target_governor: int
    skipped_governors: int
    power_ok: bool | str
    kills_ok: bool | str
    reconstruction_success: bool | str
    remaining_sec: float
    current_time: datetime.datetime = datetime.datetime.now().astimezone()

    def eta(self) -> str:
        return format_timedelta_to_HHMMSS(
            datetime.timedelta(seconds=self.remaining_sec)
        )
