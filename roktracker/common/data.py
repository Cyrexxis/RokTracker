"""Shared scan data models used across kingdom and rankings scanners.

Provides progress and timing data classes plus utility functions
for ETA formatting that the scanners use to report progress."""

import datetime
from dataclasses import dataclass, field

from roktracker.utils.general import format_timedelta_to_HHMMSS


@dataclass
class AdditionalScanData:
    """Progress and timing data for running scans."""

    current_governor: int = 0
    target_governor: int = 300
    remaining_sec: float = 0.0
    current_time: datetime.datetime = field(default_factory=datetime.datetime.now)

    def eta(self) -> str:
        """Format remaining time as HH:MM:SS.

        Returns:
            str: Remaining time formatted as hours, minutes, and seconds.
        """
        return format_timedelta_to_HHMMSS(
            datetime.timedelta(seconds=self.remaining_sec)
        )

    def current_time_str(self) -> str:
        """Format the current time as HH:MM:SS.

        Returns:
            str: Current timestamp formatted as hours, minutes, and seconds.
        """
        return self.current_time.strftime("%H:%M:%S")
