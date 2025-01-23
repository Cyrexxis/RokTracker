import math
from pydantic import BaseModel, computed_field

from roktracker.utils.general import is_string_int, to_int_check


class GovernorData(BaseModel):
    id: int | str = "Skipped"
    name: str = "Skipped"
    power: int | str = "Skipped"
    killpoints: int | str = "Skipped"
    alliance: str = "Skipped"
    t1_kills: int | str = "Skipped"
    t1_kp: int | str = "Skipped"
    t2_kills: int | str = "Skipped"
    t2_kp: int | str = "Skipped"
    t3_kills: int | str = "Skipped"
    t3_kp: int | str = "Skipped"
    t4_kills: int | str = "Skipped"
    t4_kp: int | str = "Skipped"
    t5_kills: int | str = "Skipped"
    t5_kp: int | str = "Skipped"
    ranged_points: int | str = "Skipped"
    dead: int | str = "Skipped"
    rss_assistance: int | str = "Skipped"
    rss_gathered: int | str = "Skipped"
    helps: int | str = "Skipped"

    @computed_field
    @property
    def t45_kills(self) -> int | str:
        if self.t4_kills != "Skipped" and self.t5_kills != "Skipped":
            return str(to_int_check(self.t4_kills) + to_int_check(self.t5_kills))
        else:
            return "Skipped"

    @computed_field
    @property
    def total_kills(self) -> int | str:
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
                + to_int_check(self.t45_kills)
            )
        else:
            return "Skipped"

    def flag_unknown(self):
        for field in self.model_fields:
            if getattr(self, field) == "":
                setattr(self, field, "Unknown")

    @staticmethod
    def intify_value(value: int | str) -> int:
        if isinstance(value, int):
            return value
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
