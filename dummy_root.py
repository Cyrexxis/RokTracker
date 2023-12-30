import sys
from pathlib import Path


def get_app_root():
    if getattr(sys, "frozen", False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent
