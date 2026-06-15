"""Handler for collecting and saving ranking scan data.

Maintains an in-memory list of ranking entries, checks batches
for duplicates against the last 5 entries, and writes collected
data to configured output formats with optional summary rows."""

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
    """Collects and saves ranking scan data."""

    def __init__(
        self,
        path: str | PathLike[Any],
        filename: str,
        formats: OutputFormats,
        title: str = str(date.today()),
    ):
        """Creates a ranking data handler.

        Args:
            path (str | PathLike[Any]): The folder to use for saving the data
            filename (str): The name of the file to save without extension
            formats (OutputFormats): The formats to use for saving the data
            title (str): Only used for the xlsx file - the name of the sheet (Default value = str(date.today()))
        """
        self.title = title
        self.path = pathlib.Path(path)
        self.name = filename
        self.formats = formats
        self.data_list: list[dict[str, str | int]] = []
        self.last_score: int = -2

    def write_governors(self, gov_data: list[RankingData]) -> bool:
        """Adds a batch to the in-memory data list.

        Args:
            gov_data (list[RankingData]): The batch to add

        Returns:
            bool: True if there were duplicates in the list
        """
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
        """Check if the given governor is a duplicate of one of the last 5.

        Args:
            governor (RankingData): The governor to check

        Returns:
            bool: True if the governor is a duplicate
        """
        if len(self.data_list) == 0:
            return False

        # look at the last 5 governors
        for data in self.data_list[-min(len(self.data_list), 5) :]:
            if data["Name"] == governor.name and data["Score"] == to_int_or(
                governor.score, -1
            ):
                return True

        return False

    def save(self, trim_to: int = 0, sum_total: bool = False):
        """Save the collected data to the configured output format(s).

        Args:
            trim_to (int): The amount of governors to save, 0 means all (Default value = 0)
            sum_total (bool): Whether to add a sum at the end of the files (Default value = False)
        """
        frame = pd.DataFrame(self.data_list)
        # do trimming
        if trim_to > 0:
            frame = frame.head(trim_to)

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
