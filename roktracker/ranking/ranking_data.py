import datetime
from dataclasses import dataclass

from roktracker.utils.general import format_timedelta_to_HHMMSS


@dataclass
class RankingData:
    img_path: str
    name: str
    score: str


@dataclass
class AdditionalRankingData:
    current_page: int
    target_governor: int
    govs_per_page: int
    remaining_sec: float
    current_time: str = datetime.datetime.now().strftime("%H:%M:%S")

    def eta(self) -> str:
        return format_timedelta_to_HHMMSS(
            datetime.timedelta(seconds=self.remaining_sec)
        )
