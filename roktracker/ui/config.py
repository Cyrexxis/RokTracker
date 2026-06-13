"""
Global configuration module for the rok tracker application
"""

from typing import Literal

from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from dummy_root import get_app_root

AVAILABLE_THEMES: list[str] = [
    "cosmo",
    "flatly",
    "litera",
    "minty",
    "lumen",
    "sandstone",
    "yeti",
    "pulse",
    "united",
    "morph",
    "journal",
    "darkly",
    "superhero",
    "solar",
    "cyborg",
    "vapor",
    "simplex",
    "cerculean",
]


class GUIConfig(BaseSettings):
    """
    This is the collection of all globally configured values.
    It uses default values or loads from the config.json file.
    """

    model_config = SettingsConfigDict(
        json_file=get_app_root() / "config" / "gui_config.json", extra="ignore"
    )

    default_theme: Literal[
        "cosmo",
        "flatly",
        "litera",
        "minty",
        "lumen",
        "sandstone",
        "yeti",
        "pulse",
        "united",
        "morph",
        "journal",
        "darkly",
        "superhero",
        "solar",
        "cyborg",
        "vapor",
        "simplex",
        "cerculean",
    ] = "darkly"

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
