"""Application setup validation utilities.

Provides validate_installation() to check that all required
files are present, and sanitize_scan_name() to produce valid
filenames from user input."""

import glob
import logging
import os
from dataclasses import dataclass
from typing import List

from pathvalidate import ValidationError, sanitize_filename, validate_filename

from dummy_root import get_app_root
from roktracker.utils.console import console

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """A result of a validation.

    Attributes:
        success (bool): True if successful
        messages (List[str]): The messages if validation failed
    """

    success: bool
    messages: List[str]


@dataclass
class SanitizationResult:
    """A result of a sanitization.

    Attributes:
        valid (bool): True if valid
        messages (List[str]): The messages if validation failed
        result (str): The resulting string
    """

    valid: bool
    messages: List[str]
    result: str


def validate_installation() -> ValidationResult:
    """Validates if all necessary files are present.

    Returns:
        ValidationResult: Validation result
    """
    result: List[str] = []
    root_dir = get_app_root()

    tess_dir = root_dir / "deps" / "tessdata"
    adb_dir = root_dir / "deps" / "platform-tools"

    tessdata_present = False
    adb_present = False

    if os.path.exists(tess_dir):
        tessdata_present = True
        available_trainingdata = glob.glob(str(tess_dir / "*.traineddata"))
        if len(available_trainingdata) == 0:
            title = "Tess dir found, but no training data is present"
            result.append(title)
            console.log(title)
            logger.critical(title)

            message = f"It is expected that you put the training files for tesseract in this folder: {tess_dir}"
            result.append(message)
            console.log(message)
            logger.info(message)
            tessdata_present = False
    else:
        title = "Tess dir is missing"
        result.append(title)
        console.log(title)
        logger.critical(title)

        message = f"It is expected that you create the folder ({tess_dir}) and put the training files for tesseract in it."
        result.append(message)
        console.log(message)
        logger.info(message)
        tessdata_present = False

    if os.path.exists(adb_dir):
        adb_present = True
        if not os.path.isfile(adb_dir / "adb.exe"):
            title = "Adb dir found, but adb.exe missing"
            result.append(title)
            console.log(title)
            logger.critical(title)

            message = f"It is expected that your adb.exe file is located in this folder: {adb_dir}"
            result.append(message)
            console.log(message)
            logger.info(message)
            adb_present = False
    else:
        title = "Adb dir is missing"
        result.append(title)
        console.log(title)
        logger.critical(title)

        message = f"It is expected that you create the folder ({adb_dir}) and put extract the downloaded platform tools into it."
        result.append(message)
        console.log(message)
        logger.info(message)
        adb_present = False

    return ValidationResult(tessdata_present and adb_present, result)


def sanitize_scan_name(filename: str) -> SanitizationResult:
    """Sanitizes the scan name to a valid file name.

    Args:
        filename (str): String to validate

    Returns:
        SanitizationResult: The result of the validation
    """
    if filename == "":
        return SanitizationResult(True, [], "")

    valid = True
    result = ""
    errors: List[str] = []

    try:
        validate_filename(filename)
    except ValidationError as e:
        valid = False
        message = f"Scan name validation error: {e}"
        errors.append(message)
        console.log(message)
        logger.info(message)

    try:
        result = str(sanitize_filename(filename))
    except ValidationError as e:
        valid = False
        message = f"Scan name validation error: {e}"
        errors.append(message)
        console.log(message)
        logger.info(message)

    return SanitizationResult(valid, errors, result)
