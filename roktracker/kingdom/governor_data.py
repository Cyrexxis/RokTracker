import math

from dataclasses import dataclass
from roktracker.utils.general import is_string_int, to_int_check


@dataclass
class GovernorData:
    id: str = "Skipped"
    name: str = "Skipped"
    power: str = "Skipped"
    killpoints: str = "Skipped"
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
        if self.t4_kills != "Skipped" and self.t5_kills != "Skipped":
            return str(to_int_check(self.t4_kills) + to_int_check(self.t5_kills))
        else:
            return "Skipped"

    def total_kills(self) -> str:
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

    def flag_unknown(self):
        if self.power == "":
            self.power = "Unknown"

        if self.killpoints == "":
            self.killpoints = "Unknown"

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
        if value == "Unknown":
            return -1
        elif value == "Skipped":
            return -2
        elif not is_string_int(value):
            return -3
        else:
            return int(value)

    def validate_kills(self) -> bool:
        expectedKp = (
            math.floor(to_int_check(self.t1_kills) * 0.2)
            + (to_int_check(self.t2_kills) * 2)
            + (to_int_check(self.t3_kills) * 4)
            + (to_int_check(self.t4_kills) * 10)
            + (to_int_check(self.t5_kills) * 20)
        )

        return to_int_check(self.killpoints) == expectedKp

    def validate_killpoints(self) -> bool:
        expectedKp = (
            to_int_check(self.t1_kp)
            + to_int_check(self.t2_kp)
            + to_int_check(self.t3_kp)
            + to_int_check(self.t4_kp)
            + to_int_check(self.t5_kp)
        )
        return to_int_check(self.killpoints) == expectedKp

    def reconstruct_kills(self) -> bool:
        # Kills can only reconstructed if kp are correct
        if self.validate_killpoints():
            kills_t1 = to_int_check(self.t1_kp) / 0.2

            if (
                kills_t1 < to_int_check(self.t1_kp) <= (kills_t1 + 4)
            ):  # fix t1 kills if no error is present
                kills_t1 = to_int_check(self.t1_kp)
            elif (
                kills_t1 % 10 < to_int_check(self.t1_kp) % 10 <= (kills_t1 + 4) % 10
            ):  # try to fix t1 with error (assuming last digit is correct)
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
