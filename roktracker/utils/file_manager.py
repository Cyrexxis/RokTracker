import json
from typing import List

from pydantic import TypeAdapter
from dummy_root import get_app_root
from roktracker.utils.exceptions import ConfigError
from roktracker.utils.types.full_config import FullConfig
from roktracker.utils.types.scan_preset import ScanPreset


def load_config() -> FullConfig:
    try:
        with open(get_app_root() / "config.json", "rt") as config_file:
            return FullConfig(**json.load(config_file))
    except json.JSONDecodeError as e:
        if e.msg == "Invalid \\escape":
            raise ConfigError(
                f"Config is invalid. Make sure you use \\\\ instead of \\. The error happened in line {e.lineno}."
            )
        if e.msg == "Invalid control character at":
            raise ConfigError(
                f"Config is invalid. {e.msg} char {e.colno} in line {e.lineno}."
            )
        raise ConfigError(f"Config is invalid. {e.msg} in line {e.lineno}.")
    except FileNotFoundError:
        raise ConfigError(
            "Config file is missing: make sure config.json is in the same folder as your scanner."
        )


def load_kingdom_presets() -> List[ScanPreset]:
    try:
        with open(get_app_root() / "presets.json", "rt") as preset_file:
            return TypeAdapter(list[ScanPreset]).validate_json(preset_file.read())
    except json.JSONDecodeError as e:
        if e.msg == "Invalid \\escape":
            raise ConfigError(
                f"Presets are invalid. Make sure you use \\\\ instead of \\. The error happened in line {e.lineno}."
            )
        if e.msg == "Invalid control character at":
            raise ConfigError(
                f"Presets are invalid. {e.msg} char {e.colno} in line {e.lineno}."
            )
        raise ConfigError(f"Presets are invalid. {e.msg} in line {e.lineno}.")
    except FileNotFoundError:
        return []


def save_kingdom_presets(presets: List[ScanPreset]):
    with open(get_app_root() / "presets.json", "wt") as preset_file:
        preset_file.write(TypeAdapter(list[ScanPreset]).dump_json(presets).decode())
