from os import PathLike
from typing import Any
import pandas as pd
import pathlib

from roktracker.kingdom.governor_data import GovernorData
from roktracker.utils.output_formats import OutputFormats
from datetime import date


class PandasHandler:
    def __init__(
        self,
        path: str | PathLike[Any],
        filename: str,
        formats: OutputFormats,
        title: str = str(date.today()),
    ):
        self.title = title
        self.path = pathlib.Path(path)
        self.name = filename
        self.formats = formats
        self.data_list = []

    def write_governor(self, gov_data: GovernorData) -> None:
        self.data_list.append(
            {
                "ID": GovernorData.intify_value(gov_data.id),
                "Name": gov_data.name,
                "Power": GovernorData.intify_value(gov_data.power),
                "Killpoints": GovernorData.intify_value(gov_data.killpoints),
                "Deads": GovernorData.intify_value(gov_data.dead),
                "T1 Kills": GovernorData.intify_value(gov_data.t1_kills),
                "T2 Kills": GovernorData.intify_value(gov_data.t2_kills),
                "T3 Kills": GovernorData.intify_value(gov_data.t3_kills),
                "T4 Kills": GovernorData.intify_value(gov_data.t4_kills),
                "T5 Kills": GovernorData.intify_value(gov_data.t5_kills),
                "Total Kills": GovernorData.intify_value(gov_data.total_kills()),
                "T45 Kills": GovernorData.intify_value(gov_data.t45_kills()),
                "Ranged": GovernorData.intify_value(gov_data.ranged_points),
                "Rss Gathered": GovernorData.intify_value(gov_data.rss_gathered),
                "Rss Assistance": GovernorData.intify_value(gov_data.rss_assistance),
                "Helps": GovernorData.intify_value(gov_data.helps),
                "Alliance": gov_data.alliance.rstrip(),
            }
        )

    def is_duplicate(self, gov_id: int) -> bool:
        if len(self.data_list) == 0:
            return False
        elif self.data_list[-1]["ID"] == gov_id:
            return True
        else:
            return False

    def save(self):
        frame = pd.DataFrame(self.data_list)
        # Drop cols that contain skipped values
        frame = frame.loc[:, ~(frame == -2).any()]

        if self.formats.csv:
            frame.to_csv(self.path / (self.name + ".csv"), index=False)

        if self.formats.jsonl:
            frame.to_json(
                self.path / (self.name + ".jsonl"),
                index=False,
                lines=True,
                orient="records",
                force_ascii=False,
            )

        if self.formats.xlsx:
            frame.to_excel(
                self.path / (self.name + ".xlsx"), index=False, sheet_name=self.title
            )
