import json
import os
import sys
from threading import Event
import dummy_root
import webview
import getpass

# Import Bottle
from bottle import static_file, Bottle

from roktracker.kingdom.additional_data import AdditionalData
from roktracker.kingdom.governor_data import GovernorData
from roktracker.kingdom.scanner import KingdomScanner, scan_preset_to_scan_options
from roktracker.utils.types.full_config import FullConfig
from roktracker.utils.types.scan_preset import ScanPreset

MAIN_DIR = os.path.join(dummy_root.get_script_root(), "dist", "spa")

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


DEBUG = True

js_confirm_result = False
jsResponse = Event()


class ScanCallbackHandler:
    def CallJavascript(self, js):
        window.evaluate_js(js)
        return ""

    def kingdom_governor_callback(
        self, gov_data: GovernorData, extra_data: AdditionalData
    ) -> None:
        pass

    def state_callback(self, state: str) -> None:
        pass

    def ask_confirm(self, message: str) -> bool:
        jsResponse.clear()

        # Call the JavaScript dialog through webview
        window.evaluate_js("window.kingdom.askConfirm('Do you want to continue?')")

        # Wait for response
        jsResponse.wait()
        return js_confirm_result


scanCbHandler = ScanCallbackHandler()


class API:
    def __init__(self):
        self.username = getpass.getuser()

    def GetUsername(self):
        return {"user": self.username}

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
        global kingdom_scanner
        config = FullConfig(**json.loads(full_config))
        preset = ScanPreset(**json.loads(scan_preset))
        kingdom_scanner = KingdomScanner(
            config, scan_preset_to_scan_options(preset), config.general.adb_port
        )
        kingdom_scanner.set_governor_callback(scanCbHandler.kingdom_governor_callback)
        kingdom_scanner.set_state_callback(scanCbHandler.state_callback)
        kingdom_scanner.set_continue_handler(scanCbHandler.ask_confirm)

        # Update UUID here

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

        return ""


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

    webview.start(debug=DEBUG, http_server=True)


if __name__ == "__main__":
    WebViewApp()
