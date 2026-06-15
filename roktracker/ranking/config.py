"""Pydantic models for ranking scanner configuration.

Defines OCR preprocessing settings, per-batch region-of-interest
coordinates, and the ranking config model. Supports loading
from JSON via the from_json() class method."""

from pathlib import Path

from pydantic import BaseModel


class RankingMisc(BaseModel):
    """Additional info how to handle the scan.

    Attributes:
        threshold (int): The threshold value to use when preprocessing the image
        invert (bool): Whether to invert the image before OCR
        script (str): A script name to use for scrolling after each batch
    """

    threshold: int
    invert: bool
    script: str


class UIConfig(BaseModel):
    """UI configuration for a batch on the ranking screen.

    Attributes:
        name_normal (list[tuple[int, int, int, int]]): The ROI where the name is located normally
        score_normal (list[tuple[int, int, int, int]]): The ROI where the score is located normally
        name_last (list[tuple[int, int, int, int]]): The ROI where the name is located when at the end of the rankings
        score_last (list[tuple[int, int, int, int]]): The ROI where the score is located when at the end of the rankings
    """

    name_normal: list[tuple[int, int, int, int]]
    score_normal: list[tuple[int, int, int, int]]

    name_last: list[tuple[int, int, int, int]]
    score_last: list[tuple[int, int, int, int]]


class RankingConfig(BaseModel):
    """Config options related to a ranking scan."""

    scan_path: str  # e.g. "scans_alliance"
    filename_prefix: str  # e.g. "Alliance"
    govs_per_screen: int  # e.g. 6
    last_different: bool  # True for Alliance/Seed (normal+last ROIs), False for Honor
    ui_config: UIConfig  # Any UI class with .name, .score, .name_last, etc.
    misc: RankingMisc

    @staticmethod
    def from_json(path: str | Path) -> RankingConfig:
        """Load and validate a RankingConfig from a JSON file.

        Args:
            path (str | Path): A string or Path object to the json file

        Returns:
            RankingConfig: The loaded and validated RankingConfig
        """
        data = Path(path).read_text(encoding="utf-8")
        return RankingConfig.model_validate_json(data)
