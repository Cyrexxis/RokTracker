import logging
import sys


from roktracker.utils.console import console
from typing import Tuple

logger = logging.getLogger(__name__)


def check_py_version(required_version: Tuple[int, int]) -> bool:
    current_version = sys.version_info

    if current_version < required_version:
        console.log(
            f"Update required: Current Python version is {current_version.major}.{current_version.minor} "
            f"but version {required_version[0]}.{required_version[1]} or higher is needed."
        )
        logger.warning(
            f"Update required: Current Python version is {current_version.major}.{current_version.minor} "
            f"but version {required_version[0]}.{required_version[1]} or higher is needed."
        )
        return False
    else:
        return True
