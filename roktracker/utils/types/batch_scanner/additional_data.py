import datetime

from pydantic import BaseModel

from roktracker.utils.general import format_timedelta_to_HHMMSS


class AdditionalData(BaseModel):
    current_page: int
    govs_per_page: int
    target_governor: int
    remaining_sec: float
    current_time: datetime.datetime = datetime.datetime.now().astimezone()

    def eta(self) -> str:
        return format_timedelta_to_HHMMSS(
            datetime.timedelta(seconds=self.remaining_sec)
        )
