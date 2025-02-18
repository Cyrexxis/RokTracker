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


def get_script_root():
    if getattr(sys, "frozen", False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        return Path(sys._MEIPASS)  # type: ignore
    else:
        return Path(__file__).parent


def get_web_root():
    if getattr(sys, "frozen", False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        return get_script_root() / "dist" / "spa"
    else:
        return get_script_root() / "gui_frontend" / "dist" / "spa"
