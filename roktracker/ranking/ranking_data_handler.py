import logging
import pathlib
from datetime import date
from os import PathLike
from typing import Any

import pandas as pd

from roktracker.common.output_formats import OutputFormats
from roktracker.ranking.ranking_data import RankingData
from roktracker.utils.general import to_int_or

logger = logging.getLogger(__name__)


class RankingDataHandler:
    def __init__(
        self,
        path: str | PathLike[Any],
        filename: str,
        formats: OutputFormats,
        title: str = str(date.today()),
        extra_data_fields: list[str] | None = None,
    ):
        self.title = title
        self.path = pathlib.Path(path)
        self.name = filename
        self.formats = formats
        self.extra_data_fields = extra_data_fields or []
        self.data_list: list[dict[str, str | int]] = []
        self.last_score: int = -2

    def write_governors(self, gov_data: list[RankingData]) -> bool:
        """Write a batch of governor data. Returns True if the last screen is reached."""
        reached_bottom = False

        for gov in gov_data:
            if not self.is_duplicate(gov):
                int_score = to_int_or(gov.score, -1)
                if self.last_score == -2 and int_score != -1:
                    self.last_score = int_score
                elif int_score == -1:
                    logger.warning(
                        f"Error in score detected (score not readable) at rank {len(self.data_list)}"
                    )
                    int_score = self.last_score
                elif int_score > self.last_score:
                    logger.warning(
                        f"Error in score detected (score too high) at rank {len(self.data_list)}"
                    )
                    int_score = self.last_score
                else:
                    self.last_score = int_score

                # Insert gov if not duplicate
                self.data_list.append(
                    {
                        "Image": gov.img_path,
                        "Name": gov.name,
                        "Score": int_score,
                    }
                )
            else:
                # Duplicated govs can only happen on last page
                reached_bottom = True

        return reached_bottom

    def is_duplicate(self, governor: RankingData) -> bool:
        """Check whether `governor` is a duplicate of a recently written entry."""
        if len(self.data_list) == 0:
            return False

        # look at the last 5 governors
        for data in self.data_list[-min(len(self.data_list), 5) :]:
            if data["Name"] == governor.name and data["Score"] == to_int_or(
                governor.score, -1
            ):
                return True

        return False

    def save(self, trimm_to: int = 0, sum_total: bool = False):
        frame = pd.DataFrame(self.data_list)
        # do trimming
        if trimm_to > 0:
            frame = frame.head(trimm_to)

        # strip the image path
        frame_stripped = frame.drop("Image", axis=1)
        frame_stripped = frame_stripped.set_index("Name", drop=False)

        # add sum
        if sum_total:
            frame_stripped.loc["Total"] = frame_stripped.sum(numeric_only=True, axis=0)
            frame_stripped.at["Total", "Name"] = "Total"

        if self.formats.csv:
            frame_stripped.to_csv(self.path / (self.name + ".csv"), index=False)

        if self.formats.jsonl:
            frame_stripped.to_json(
                self.path / (self.name + ".jsonl"),
                index=False,
                lines=True,
                orient="records",
                force_ascii=False,
            )

        if self.formats.xlsx:
            with pd.ExcelWriter(
                self.path / (self.name + ".xlsx"), engine="xlsxwriter"
            ) as writer:
                frame_stripped.to_excel(
                    writer, index=False, sheet_name=self.title, startcol=1
                )

                worksheet = writer.sheets[self.title]
                worksheet.set_default_row(24.75)
                worksheet.set_column(0, 0, 42)
                for index, row in frame.iterrows():
                    excel_row = int(index.__str__()) + 2
                    worksheet.insert_image(
                        f"A{excel_row}", row["Image"], {"y_offset": 5}
                    )
