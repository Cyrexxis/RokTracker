"""Global configuration and settings for the rok tracker application.

Defines the AppConfig and related configuration models loaded
from config.json, with default values for emulator type, ADB
port, and Bluestacks paths."""

from pathlib import Path
from typing import Literal, override

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from dummy_root import get_app_root


class ScanTimings(BaseModel):
    """Waiting timings between ADB actions during kingdom scanning."""

    gov_open: float = 2.0
    copy_wait: float = 0.2
    kills_open: float = 1.0
    info_open: float = 1.0
    info_close: float = 0.5
    gov_close: float = 1.0
    max_random: float = 0.5


class BluestacksConfig(BaseModel):
    """Configuration specific to the Bluestacks emulator."""

    name: str = "RoK Tracker"
    config: str = str(Path("C:/ProgramData/Bluestacks_nxt/bluestacks.conf"))


class GeneralConfig(BaseModel):
    """General application settings (emulator type, ADB port, etc.)."""

    emulator: Literal["bluestacks", "ld"] = "bluestacks"
    adb_port: int = 5555
    bluestacks: BluestacksConfig = BluestacksConfig()


class AppConfig(BaseSettings):
    """Collection of all globally configured values.

    It uses default values or loads from the config.json file.
    """

    model_config = SettingsConfigDict(
        # Load settings from config.json; silently ignore unknown keys.
        json_file=get_app_root() / "config" / "config.json",
        extra="ignore",
    )

    timings: ScanTimings = ScanTimings()
    general: GeneralConfig = GeneralConfig()

    @override
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Only load settings from the JSON config file, ignoring env vars.

        Args:
            settings_cls (type[BaseSettings]): pydantic internal
            init_settings (PydanticBaseSettingsSource): pydantic internal
            env_settings (PydanticBaseSettingsSource): pydantic internal
            dotenv_settings (PydanticBaseSettingsSource): pydantic internal
            file_secret_settings (PydanticBaseSettingsSource): pydantic internal

        Returns:
            tuple[PydanticBaseSettingsSource, ...]: pydantic internal
        """
        return (JsonConfigSettingsSource(settings_cls),)
