import logging
import sys
import threading

import ttkbootstrap as ttk

from dummy_root import get_app_root
from roktracker.common.config import AppConfig
from roktracker.ui.kingdom_scanner_ui import KingdomScannerUI
from roktracker.utils.exception_handling import GuiExceptionHandler

logging.basicConfig(
    filename=str(get_app_root() / "scanner.log"),
    encoding="utf-8",
    format="%(asctime)s %(module)s %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
ex_handler = GuiExceptionHandler(logger)

sys.excepthook = ex_handler.handle_exception
threading.excepthook = ex_handler.handle_thread_exception

root = ttk.Window(title="ROK Scanner by Cyrexxis", themename="darkly")
kingdom_scanner = KingdomScannerUI(root, AppConfig())
kingdom_scanner.pack(padx=5, pady=5)

root.mainloop()
