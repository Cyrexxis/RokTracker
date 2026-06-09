"""
Global configuration module for the rok tracker application
"""

from typing import Literal

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from dummy_root import get_app_root


class ScanTimings(BaseModel):
    gov_open: float = 2.0
    copy_wait: float = 0.2
    kills_open: float = 1.0
    info_open: float = 1.0
    info_close: float = 0.5
    gov_close: float = 1.0
    max_random: float = 0.5


class BluestacksConfig(BaseModel):
    name: str = "RoK Tracker"
    config: str = "C:\\ProgramData\\Bluestacks_nxt\\bluestacks.conf"


class GeneralConfig(BaseModel):
    emulator: Literal["bluestacks", "ld"] = "bluestacks"
    adb_port: int = 5555
    bluestacks: BluestacksConfig = BluestacksConfig()


class AppConfig(BaseSettings):
    """
    This is the collection of all globally configured values.
    It uses default values or loads from the config.json file.
    """

    model_config = SettingsConfigDict(
        json_file=get_app_root() / "config.json", extra="ignore"
    )

    timings: ScanTimings = ScanTimings()
    general: GeneralConfig = GeneralConfig()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (JsonConfigSettingsSource(settings_cls),)
