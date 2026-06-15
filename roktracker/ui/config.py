"""Global GUI configuration for the rok tracker application.

Provides the GUIConfig class with default values loaded from
config.json. Ignores environment variables to enforce file-based
configuration only."""

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
"""The list of all supported themes."""


class GUIConfig(BaseSettings):
    """A collection of all globally configured values.

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
