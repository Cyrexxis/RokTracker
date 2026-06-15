"""Data models for governor scan results and aggregated scan progress.

Provides the GovernorData model for OCR-extracted governor data,
the AdditionalGovernorData progress model, and utility functions
for kill validation and point reconstruction"""

import math
from dataclasses import dataclass

from roktracker.common.data import AdditionalScanData
from roktracker.utils.general import (
    is_string_int,
    to_int_check,
)


@dataclass
class GovernorData:
    """Represents the OCR-extracted data for a single governor.

    The type of all attributes is str because the class is intended
    to be used to show the the current state to the user.

    For data handling purposes the data can be converted to int using the
    intify method, that maps invalid data to negative values.
    """

    id: str = "Skipped"
    name: str = "Skipped"
    power: str = "Skipped"
    killpoints: str = "Skipped"
    acclaim: str = "Skipped"
    acclaim_max: str = "Skipped"
    alliance: str = "Skipped"
    t1_kills: str = "Skipped"
    t1_kp: str = "Skipped"
    t2_kills: str = "Skipped"
    t2_kp: str = "Skipped"
    t3_kills: str = "Skipped"
    t3_kp: str = "Skipped"
    t4_kills: str = "Skipped"
    t4_kp: str = "Skipped"
    t5_kills: str = "Skipped"
    t5_kp: str = "Skipped"
    ranged_points: str = "Skipped"
    dead: str = "Skipped"
    rss_assistance: str = "Skipped"
    rss_gathered: str = "Skipped"
    helps: str = "Skipped"

    def t45_kills(self) -> str:
        """Sum of tier 4 and tier 5 kills.

        Returns:
            str: Total kills or "Skipped" if either tier is unavailable.
        """
        if self.t4_kills != "Skipped" and self.t5_kills != "Skipped":
            return str(to_int_check(self.t4_kills) + to_int_check(self.t5_kills))
        else:
            return "Skipped"

    def total_kills(self) -> str:
        """Sum of all tier kills.

        Returns:
            str: Total kills across all tiers or "Skipped" if any tier is unavailable.
        """
        if (
            self.t1_kills != "Skipped"
            and self.t2_kills != "Skipped"
            and self.t3_kills != "Skipped"
            and self.t4_kills != "Skipped"
            and self.t5_kills != "Skipped"
        ):
            return str(
                to_int_check(self.t1_kills)
                + to_int_check(self.t2_kills)
                + to_int_check(self.t3_kills)
                + to_int_check(self.t45_kills())
            )
        else:
            return "Skipped"

    def flag_unknown(self) -> None:
        """Replace empty fields with "Unknown".

        This must be called before writing to avoid pandas coercing empty strings
        to NaN in the output.
        """
        if self.power == "":
            self.power = "Unknown"

        if self.killpoints == "":
            self.killpoints = "Unknown"

        if self.acclaim == "":
            self.acclaim = "Unknown"

        if self.acclaim_max == "":
            self.acclaim_max = "Unknown"

        if self.t1_kills == "":
            self.t1_kills = "Unknown"

        if self.t2_kills == "":
            self.t2_kills = "Unknown"

        if self.t3_kills == "":
            self.t3_kills = "Unknown"

        if self.t4_kills == "":
            self.t4_kills = "Unknown"

        if self.t5_kills == "":
            self.t5_kills = "Unknown"

        if self.t1_kp == "":
            self.t1_kp = "Unknown"

        if self.t2_kp == "":
            self.t2_kp = "Unknown"

        if self.t3_kp == "":
            self.t3_kp = "Unknown"

        if self.t4_kp == "":
            self.t4_kp = "Unknown"

        if self.t5_kp == "":
            self.t5_kp = "Unknown"

        if self.ranged_points == "":
            self.ranged_points = "Unknown"

        if self.dead == "":
            self.dead = "Unknown"

        if self.rss_gathered == "":
            self.rss_gathered = "Unknown"

        if self.rss_assistance == "":
            self.rss_assistance = "Unknown"

        if self.helps == "":
            self.helps = "Unknown"

    @staticmethod
    def intify_value(value: str) -> int:
        """Convert a governor data string to an integer for pandas export.

        Unknown values and skipped scans are mapped to sentinel values so
        pandas can drop the corresponding columns automatically.

        Here is the mapping:

        =========       =========
        String          Int
        =========       =========
        Unknown         -1
        Skipped         -2
        NaN             -3
        =========       =========

        Args:
            value (str): The string to convert

        Returns:
            int: An int value representing the string
        """
        if value == "Unknown":
            return -1
        elif value == "Skipped":
            return -2
        elif not is_string_int(value):
            return -3
        else:
            return int(value)

    def validate_kills(self) -> bool:
        """Verify that total killpoints match the sum of tier kills.

        Tier killpoint multipliers: T1=0.2, T2=2, T3=4, T4=10, T5=20.

        Returns:
            bool: True if the tier kills are correct
        """
        expected_kp = (
            math.floor(to_int_check(self.t1_kills) * 0.2)
            + (to_int_check(self.t2_kills) * 2)
            + (to_int_check(self.t3_kills) * 4)
            + (to_int_check(self.t4_kills) * 10)
            + (to_int_check(self.t5_kills) * 20)
        )

        return to_int_check(self.killpoints) == expected_kp

    def validate_killpoints(self) -> bool:
        """Verify that total killpoints equal the sum of tier killpoints.

        Returns:
            bool: True if the tier killpoints are correct
        """
        expected_kp = (
            to_int_check(self.t1_kp)
            + to_int_check(self.t2_kp)
            + to_int_check(self.t3_kp)
            + to_int_check(self.t4_kp)
            + to_int_check(self.t5_kp)
        )
        return to_int_check(self.killpoints) == expected_kp

    def reconstruct_kills(self) -> bool:
        """Reconstruct tier kills from verified tier killpoints.

        Tier killpoint multipliers: T1=0.2, T2=2, T3=4, T4=10, T5=20.
        For tier 1 a heuristic is applied to minimize rounding errors.

        Returns:
            bool: True if killpoint validation passed and kills were reconstructed,
                False otherwise.
        """
        if self.validate_killpoints():
            kills_t1 = to_int_check(self.t1_kp) / 0.2

            if kills_t1 < to_int_check(self.t1_kp) <= (kills_t1 + 4):
                # fix t1 kills if no error is present
                kills_t1 = to_int_check(self.t1_kp)
            elif kills_t1 % 10 < to_int_check(self.t1_kp) % 10 <= (kills_t1 + 4) % 10:
                # try to fix t1 with error (assuming last digit is correct)
                kill_dif_t1 = (to_int_check(self.t1_kp) % 10) - (kills_t1 % 10)
                kills_t1 = kills_t1 + kill_dif_t1

            self.t1_kills = str(kills_t1)
            self.t2_kills = str(to_int_check(self.t2_kp) / 2)
            self.t3_kills = str(to_int_check(self.t3_kp) / 4)
            self.t4_kills = str(to_int_check(self.t4_kp) / 10)
            self.t5_kills = str(to_int_check(self.t5_kp) / 20)
            return True
        else:
            return False


@dataclass(kw_only=True)
class AdditionalGovernorData(AdditionalScanData):
    """Progress data specific to a kingdom scan."""

    skipped_governors: int = 0
    power_ok: str = "True"
    kills_ok: str = "True"
    reconstruction_success: str = "True"
