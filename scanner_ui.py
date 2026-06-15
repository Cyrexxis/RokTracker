import logging
import sys
import threading

import ttkbootstrap as ttk

from dummy_root import get_app_root
from roktracker.common.config import AppConfig
from roktracker.ui.config import GUIConfig
from roktracker.ui.header_frame import HeaderFrame
from roktracker.ui.kingdom_scanner_ui import KingdomScannerUI
from roktracker.ui.ranking_scanner_ui import RankingScannerUI
from roktracker.utils.exception_handling import GuiExceptionHandler
from roktracker.utils.validator import validate_installation

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

if not validate_installation().success:
    sys.exit(2)

ui_config = GUIConfig()

root = ttk.Window(title="ROK Scanner by Cyrexxis", themename=ui_config.default_theme)

header_frame = HeaderFrame(root, ui_config.default_theme)
header_frame.pack(fill="x", padx=5, pady=(5, 0))

tab_frame = ttk.Notebook(root)
tab_frame.pack(padx=5, pady=5)
tab_frame.add(KingdomScannerUI(tab_frame, AppConfig()), text="Kingdom")
tab_frame.add(RankingScannerUI(tab_frame, AppConfig()), text="Rankings")

root.mainloop()
