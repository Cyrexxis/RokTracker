"""General utility functions for conversions, image I/O, and helpers.

Provides type conversion (to_int_check, to_int_or, is_string_int/
float), timing (wait_random_range, format_timedelta_to_HHMMSS),
image loading (load_cv2_img, write_cv2_img) for UTF-8 paths,
and other misc helpers (generate_random_id, more_info_present)."""

import datetime
import random
import string
import time
from os import PathLike
from typing import Any

import cv2
import numpy as np
from cv2.typing import MatLike


def to_int_check(element: str) -> int:
    """Converts a string to an int.

    Args:
        element (str): String to convert

    Returns:
        int: Int representation of string or 0 if not convertible
    """
    try:
        return int(element)
    except ValueError:
        # return dummy 0
        return int(0)


def to_int_or(element: Any, fallback: int) -> int:
    """Converts any element to an int or a fallback value when conversion fails.

    Args:
        element (Any): Element to convert
        fallback (int): Default value when failing

    Returns:
        int: The Int representation
    """
    try:
        return int(element)
    except ValueError:
        # return dummy 0
        return int(fallback)


def is_string_int(element: str, allow_empty: bool = False) -> bool:
    """Returns whether a string is an int.

    Args:
        element (str): String to check
        allow_empty (bool): Whether empty string passes or not (Default value = False)

    Returns:
        bool: True if string can be converted, False otherwise
    """
    if allow_empty and element == "":
        return True

    try:
        _ = int(element)
        return True
    except ValueError:
        return False


def is_string_float(element: str, allow_empty: bool = False) -> bool:
    """Returns whether a string is a float.

    Args:
        element (str): String to check
        allow_empty (bool): Whether empty string passes or not (Default value = False)

    Returns:
        bool: True if string can be converted, False otherwise
    """
    if allow_empty and element == "":
        return True

    try:
        _ = float(element)
        return True
    except ValueError:
        return False


def more_info_present(ocr_text: str) -> bool:
    """Checks if more info is contained in the text.

    It also checks some other common results of the OCR engine

    Args:
        ocr_text (str): String to check

    Returns:
        bool: True if more info is found, False otherwise
    """
    return "MoreInfo" in ocr_text or "Moren" in ocr_text


def generate_random_id(length: int) -> str:
    """Generates a random ID with the given length.

    Args:
        length (int): The length of the id

    Returns:
        str: The generated id
    """
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choices(alphabet, k=length))


def wait_random_range(min_time: float, max_offset: float) -> None:
    """Waits for a random amount within the given limits.

    Has a low chance to wait much longer to simulate human behavior (1 in 20 times)

    Args:
        min_time (float): The minimum time to wait
        max_offset (float): The max amount added to the minimum time
    """
    extra = random.uniform(1.5, 4.0) if random.random() < 0.05 else 0.0
    time.sleep(random.uniform(min_time, min_time + max_offset) + extra)


def format_timedelta_to_HHMMSS(td: datetime.timedelta) -> str:
    """Formats a timedelta to the string representation.

    Args:
        td (datetime.timedelta): Timedelta to format

    Returns:
        str: The formatted delta
    """
    td_in_seconds = td.total_seconds()
    hours, remainder = divmod(td_in_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


# This workaround is needed because cv2 doesn't support UTF-8 paths
def load_cv2_img(path: str | PathLike[Any], flags: int) -> MatLike:
    """Loads an image from a path.

    To prevent issues with UTF-8 character in path the file gets
    loaded by numpy instead of cv2.

    Args:
        path (str | PathLike[Any]): The path to the image
        flags (int): The flags to use for file loading

    Returns:
        MatLike: The loaded image in correct cv2 format
    """
    image = cv2.imdecode(
        np.fromfile(file=path, dtype=np.uint8),
        flags,
    )

    if image is not None:
        return image
    else:
        return np.zeros((10, 10, 3), np.uint8)


# This workaround is needed because cv2 doesn't support UTF-8 paths
def write_cv2_img(img: MatLike, path: str | PathLike[Any], filetype: str) -> None:
    """Saves an image to a path.

    To prevent issues with UTF-8 character in path the file gets
    loaded by numpy instead of cv2.

    Args:
        img (MatLike): The image to save
        path (str | PathLike[Any]): The path to save the image to
        filetype (str): The filetype (extension) to use
    """
    is_success, im_buf_arr = cv2.imencode("." + filetype, img)

    if is_success:
        im_buf_arr.tofile(path)
