import datetime
import json
import random
import string
import time
from os import PathLike
from typing import Any

import cv2
import numpy as np
from cv2.typing import MatLike

from dummy_root import get_app_root
from roktracker.utils.exceptions import ConfigError


def load_config():
    try:
        with open(get_app_root() / "config.json", "rt") as config_file:
            return json.load(config_file)
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


def to_int_check(element: str) -> int:
    try:
        return int(element)
    except ValueError:
        # return dummy 0
        return int(0)


def to_int_or(element: Any, fallback: int) -> int:
    try:
        return int(element)
    except ValueError:
        # return dummy 0
        return int(fallback)


def is_string_int(element: str, allow_empty: bool = False) -> bool:
    if allow_empty and element == "":
        return True

    try:
        _ = int(element)
        return True
    except ValueError:
        return False


def is_string_float(element: str, allow_empty: bool = False) -> bool:
    if allow_empty and element == "":
        return True

    try:
        _ = float(element)
        return True
    except ValueError:
        return False


def more_info_present(ocr_text: str) -> bool:
    return "MoreInfo" in ocr_text or "Moren" in ocr_text


def generate_random_id(length: int) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choices(alphabet, k=length))


def next_alpha(s: str) -> str:
    return chr((ord(s.upper()) + 1 - 65) % 26 + 65)


def random_delay() -> float:
    return random.random() * 0.1


def wait_random_range(min_time: float, max_offset: float) -> None:
    # Occasionally add a longer human-like pause (roughly 1 in 20 calls)
    extra = random.uniform(1.5, 4.0) if random.random() < 0.05 else 0.0
    time.sleep(random.uniform(min_time, min_time + max_offset) + extra)


def format_timedelta_to_HHMMSS(td: datetime.timedelta) -> str:
    td_in_seconds = td.total_seconds()
    hours, remainder = divmod(td_in_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    return f"({hours:02d}, {minutes:02d}, {seconds:02d})"


# This workaroud is needed because cv2 doesn't support UTF-8 paths
def load_cv2_img(path: str | PathLike[Any], flags: int) -> MatLike:
    image = cv2.imdecode(
        np.fromfile(file=path, dtype=np.uint8),
        flags,
    )

    if image:
        return image
    else:
        return np.zeros((10, 10, 3), np.uint8)


# This workaroud is needed because cv2 doesn't support UTF-8 paths
def write_cv2_img(img: MatLike, path: str | PathLike[Any], filetype: str) -> None:
    is_success, im_buf_arr = cv2.imencode("." + filetype, img)

    if is_success:
        im_buf_arr.tofile(path)
