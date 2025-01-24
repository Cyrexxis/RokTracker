import logging
import json
import os
import sys
from threading import Event, Thread
import threading
from pydantic import TypeAdapter
import dummy_root
import webview

# Import Bottle
from bottle import static_file, Bottle

from roktracker.kingdom.types.additional_data import AdditionalData
from roktracker.kingdom.types.governor_data import GovernorData
from roktracker.kingdom.scanner import KingdomScanner, scan_preset_to_scan_options
from roktracker.utils.exception_handling import ConsoleExceptionHander
from roktracker.utils.general import load_config, load_kingdom_presets
from roktracker.utils.types.full_config import FullConfig
from roktracker.utils.types.scan_preset import ScanPreset

logging.basicConfig(
    filename=str(dummy_root.get_app_root() / "kingdom-scanner-web.log"),
    encoding="utf-8",
    format="%(asctime)s %(module)s %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
ex_handler = ConsoleExceptionHander(logger)


sys.excepthook = ex_handler.handle_exception
threading.excepthook = ex_handler.handle_thread_exception

MAIN_DIR = dummy_root.get_web_root()

print(MAIN_DIR)

app = Bottle()


@app.get("/")  # type: ignore
def index():
    return static_file("index.html", root=MAIN_DIR)


# Static files route
@app.get("/<filename:path>")  # type: ignore
def get_static_files(filename):
    """Get Static files"""
    response = static_file(filename, root=MAIN_DIR)
    if response.status_code == 404:
        return static_file("index.html", root=MAIN_DIR)
    return response


# DEBUG = True

js_confirm_result = False
jsResponse = Event()


class ScanCallbackHandler:
    def CallJavascript(self, js):
        window.evaluate_js(js)
        return ""

    def kingdom_governor_callback(
        self, gov_data: GovernorData, extra_data: AdditionalData
    ) -> None:
        window.evaluate_js(
            f"window.kingdom.governorUpdate('{gov_data.model_dump_json()}', '{extra_data.model_dump_json()}')"
        )

    def state_callback(self, state: str) -> None:
        window.evaluate_js(f"window.kingdom.stateUpdate('{state}')")

    def ask_confirm(self, message: str) -> bool:
        jsResponse.clear()

        # Call the JavaScript dialog through webview
        window.evaluate_js("window.kingdom.askConfirm('Do you want to continue?')")

        # Wait for response
        jsResponse.wait()
        return js_confirm_result

    def kingdom_scan_finished(self):
        window.evaluate_js("window.kingdom.scanFinished()")

    def set_kingdom_scan_id(self, scan_id: str):
        window.evaluate_js(f"window.kingdom.setScanID('{scan_id}')")


scanCbHandler = ScanCallbackHandler()


def start_kingdom_scanner(full_config: str, scan_preset: str):
    global kingdom_scanner
    config = FullConfig(**json.loads(full_config))
    preset = ScanPreset(**json.loads(scan_preset))
    kingdom_scanner = KingdomScanner(
        config, scan_preset_to_scan_options(preset), config.general.adb_port
    )
    kingdom_scanner.set_governor_callback(scanCbHandler.kingdom_governor_callback)
    kingdom_scanner.set_state_callback(scanCbHandler.state_callback)
    kingdom_scanner.set_continue_handler(scanCbHandler.ask_confirm)

    scanCbHandler.set_kingdom_scan_id(kingdom_scanner.run_id)

    kingdom_scanner.start_scan(
        config.scan.kingdom_name,
        config.scan.people_to_scan,
        config.scan.resume,
        config.scan.track_inactives,
        config.scan.validate_kills,
        config.scan.reconstruct_kills,
        config.scan.validate_power,
        config.scan.power_threshold,
        config.scan.formats,
    )

    scanCbHandler.kingdom_scan_finished()


class API:
    def WindowReady(self):
        if getattr(sys, "frozen", False):
            import pyi_splash  # type: ignore

            pyi_splash.close()
        return ""

    def TestPython(self):
        print(scanCbHandler.ask_confirm("Do you want to continue?"))
        window.evaluate_js("console.log('Hello from python')")
        return ""

    def ConfirmCallback(self, confirmed: bool):
        global js_confirm_result, jsResponse
        js_confirm_result = confirmed
        jsResponse.set()
        return ""

    def StartKingdomScan(self, full_config: str, scan_preset: str):
        Thread(target=start_kingdom_scanner, args=(full_config, scan_preset)).start()
        return ""

    def StopKingdomScan(self):
        kingdom_scanner.end_scan()
        return ""

    def LoadFullConfig(self):
        return load_config().model_dump_json()

    def LoadScanPresets(self):
        return TypeAdapter(list[ScanPreset]).dump_json(load_kingdom_presets()).decode()


def WebViewApp():
    api = API()
    global window
    window = webview.create_window(
        "RoK Tracker Suite",
        app,  # type: ignore
        js_api=api,
        width=1285 + 20,
        height=740 + 40,
    )

    webview.start(debug=True, http_server=False)


if __name__ == "__main__":
    WebViewApp()
