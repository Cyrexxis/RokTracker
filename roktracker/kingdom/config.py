"""Pydantic models for kingdom scanner configuration.

Defines UI region coordinates, tap coordinates, and per-profile
UI config. Supports loading configuration from JSON files via
the from_json() class method."""

from pathlib import Path

from pydantic import BaseModel


class KingdomUIRegions(BaseModel):
    """OCR region coordinates for extracting governor data from screen sections."""

    # first screen
    more_info: tuple[int, int, int, int] = (0, 0, 0, 0)
    id: tuple[int, int, int, int] = (0, 0, 0, 0)
    power: tuple[int, int, int, int] = (0, 0, 0, 0)
    killpoints: tuple[int, int, int, int] = (0, 0, 0, 0)
    acclaim: tuple[int, int, int, int] = (0, 0, 0, 0)
    acclaim_max: tuple[int, int, int, int] = (0, 0, 0, 0)
    alliance: tuple[int, int, int, int] = (0, 0, 0, 0)

    # second screen
    t1_kills: tuple[int, int, int, int] = (0, 0, 0, 0)
    t2_kills: tuple[int, int, int, int] = (0, 0, 0, 0)
    t3_kills: tuple[int, int, int, int] = (0, 0, 0, 0)
    t4_kills: tuple[int, int, int, int] = (0, 0, 0, 0)
    t5_kills: tuple[int, int, int, int] = (0, 0, 0, 0)
    t1_killpoints: tuple[int, int, int, int] = (0, 0, 0, 0)
    t2_killpoints: tuple[int, int, int, int] = (0, 0, 0, 0)
    t3_killpoints: tuple[int, int, int, int] = (0, 0, 0, 0)
    t4_killpoints: tuple[int, int, int, int] = (0, 0, 0, 0)
    t5_killpoints: tuple[int, int, int, int] = (0, 0, 0, 0)
    ranged_points: tuple[int, int, int, int] = (0, 0, 0, 0)

    # third screen
    deads: tuple[int, int, int, int] = (0, 0, 0, 0)
    gathered: tuple[int, int, int, int] = (0, 0, 0, 0)
    assisted: tuple[int, int, int, int] = (0, 0, 0, 0)
    helps: tuple[int, int, int, int] = (0, 0, 0, 0)


class KingdomTapPositions(BaseModel):
    """Tap coordinates for navigating the governor screens."""

    name: tuple[int, int] = (0, 0)
    kills: tuple[int, int] = (0, 0)
    info: tuple[int, int] = (0, 0)
    close_gov: tuple[int, int] = (0, 0)

    # third screen
    close_info: tuple[int, int] = (0, 0)


class UIConfig(BaseModel):
    """UI configuration for a governor profile."""

    profile_version: tuple[int, int, int, int]
    regions: KingdomUIRegions
    taps: KingdomTapPositions
    regions_pre_acclaim: KingdomUIRegions
    taps_pre_acclaim: KingdomTapPositions


class KingdomConfig(BaseModel):
    """Config options related to a kingdom scan."""

    scan_path: str
    filename_prefix_normal: str
    filename_prefix_continued: str
    ui_config: UIConfig

    @staticmethod
    def from_json(path: str | Path) -> KingdomConfig:
        """Load and validate a KingdomConfig from a JSON file.

        Args:
            path (str | Path): A string or Path object to the json file

        Returns:
            KingdomConfig: The loaded and validated KingdomConfig
        """
        data = Path(path).read_text(encoding="utf-8")
        return KingdomConfig.model_validate_json(data)
