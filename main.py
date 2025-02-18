import logging
import json
import os
import sys
from threading import Event, Thread
import threading
from typing import List
from pydantic import TypeAdapter
import dummy_root
import webview

# Import Bottle
from bottle import static_file, Bottle

from roktracker.alliance.scanner import AllianceScanner
from roktracker.honor.scanner import HonorScanner
from roktracker.kingdom.types.additional_data import AdditionalData
from roktracker.kingdom.types.governor_data import GovernorData
from roktracker.seed.scanner import SeedScanner
from roktracker.utils.types.batch_scanner.batch_type import BatchStatus, BatchType
from roktracker.utils.types.batch_scanner.governor_data import GovernorData as BatchData
from roktracker.utils.types.batch_scanner.additional_data import (
    AdditionalData as BatchAdditionalData,
)
from roktracker.kingdom.scanner import KingdomScanner, scan_preset_to_scan_options
from roktracker.utils.exception_handling import ConsoleExceptionHander
from roktracker.utils.file_manager import (
    load_config,
    load_kingdom_presets,
    save_kingdom_presets,
)
from roktracker.utils.types.env_parser import Environment
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

environmentVars = Environment()

print(MAIN_DIR)

if not environmentVars.development:
    global app
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


kingdom_confirm_result = False
kingdomResponse = Event()

alliance_confirm_result = False
allianceResponse = Event()


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

    def kingdom_state_callback(self, state: str) -> None:
        window.evaluate_js(f"window.kingdom.stateUpdate('{state}')")

    def ask_confirm(self, message: str) -> bool:
        kingdomResponse.clear()

        # Call the JavaScript dialog through webview
        window.evaluate_js("window.kingdom.askConfirm('Do you want to continue?')")

        # Wait for response
        kingdomResponse.wait()
        return kingdom_confirm_result

    def kingdom_scan_finished(self):
        window.evaluate_js("window.kingdom.scanFinished()")

    def set_kingdom_scan_id(self, scan_id: str):
        window.evaluate_js(f"window.kingdom.setScanID('{scan_id}')")

    def batch_update(
        self,
        batch_data: List[BatchData],
        extra_data: BatchAdditionalData,
        batch_type: BatchType,
    ):
        batch_data_encoded = TypeAdapter(list[BatchData]).dump_json(batch_data).decode()
        # additional json dump needed for proper escaping
        batch_data_encoded = json.dumps(batch_data_encoded)
        window.evaluate_js(
            f"window.batch.batchUpdate({batch_data_encoded}, '{extra_data.model_dump_json()}', '{BatchStatus(type=batch_type).model_dump_json()}')"
        )

    def alliance_scan_batch_callback(
        self, batch_data: List[BatchData], extra_data: BatchAdditionalData
    ):
        self.batch_update(batch_data, extra_data, BatchType.ALLIANCE)

    def honor_scan_batch_callback(
        self, batch_data: List[BatchData], extra_data: BatchAdditionalData
    ):
        self.batch_update(batch_data, extra_data, BatchType.HONOR)

    def seed_scan_batch_callback(
        self, batch_data: List[BatchData], extra_data: BatchAdditionalData
    ):
        self.batch_update(batch_data, extra_data, BatchType.SEED)

    def batch_state_update(self, msg: str, batch_type: BatchType):
        window.evaluate_js(
            f"window.batch.stateUpdate('{msg}', '{BatchStatus(type=batch_type).model_dump_json()}')"
        )

    def alliance_state_callback(self, msg: str):
        self.batch_state_update(msg, BatchType.ALLIANCE)

    def honor_state_callback(self, msg: str):
        self.batch_state_update(msg, BatchType.HONOR)

    def seed_state_callback(self, msg: str):
        self.batch_state_update(msg, BatchType.SEED)

    def set_batch_id(self, batch_type: BatchType, id: str):
        window.evaluate_js(
            f"window.batch.setScanID('{id}', '{BatchStatus(type=batch_type).model_dump_json()}')"
        )

    def batch_scan_finished(self, batch_type: BatchType):
        window.evaluate_js(
            f"window.batch.scanFinished('{BatchStatus(type=batch_type).model_dump_json()}')"
        )

    def alliance_scan_finished(self):
        self.batch_scan_finished(BatchType.ALLIANCE)

    def honor_scan_finished(self):
        self.batch_scan_finished(BatchType.HONOR)

    def seed_scan_finished(self):
        self.batch_scan_finished(BatchType.SEED)

    def ask_confirm_alliance(self, message: str) -> bool:
        allianceResponse.clear()

        # Call the JavaScript dialog through webview
        window.evaluate_js(
            f"window.batch.askConfirm('Do you want to continue?', {BatchStatus(type=BatchType.ALLIANCE).model_dump_json()})"
        )

        # Wait for response
        allianceResponse.wait()
        return alliance_confirm_result


scanCbHandler = ScanCallbackHandler()


def start_kingdom_scanner(full_config: str, scan_preset: str):
    global kingdom_scanner
    config = FullConfig(**json.loads(full_config))
    preset = ScanPreset(**json.loads(scan_preset))
    kingdom_scanner = KingdomScanner(
        config, scan_preset_to_scan_options(preset), config.general.adb_port
    )
    kingdom_scanner.set_governor_callback(scanCbHandler.kingdom_governor_callback)
    kingdom_scanner.set_state_callback(scanCbHandler.kingdom_state_callback)
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


def start_alliance_scanner(full_config: str):
    global alliance_scanner
    config = FullConfig(**json.loads(full_config))

    alliance_scanner = AllianceScanner(config.general.adb_port, config)
    alliance_scanner.set_batch_callback(scanCbHandler.alliance_scan_batch_callback)
    alliance_scanner.set_state_callback(scanCbHandler.alliance_state_callback)

    scanCbHandler.set_batch_id(BatchType.ALLIANCE, alliance_scanner.run_id)

    alliance_scanner.start_scan(
        config.scan.kingdom_name, config.scan.people_to_scan, config.scan.formats
    )

    scanCbHandler.alliance_scan_finished()


def start_honor_scanner(full_config: str):
    global honor_scanner
    config = FullConfig(**json.loads(full_config))

    honor_scanner = HonorScanner(config.general.adb_port, config)
    honor_scanner.set_batch_callback(scanCbHandler.honor_scan_batch_callback)
    honor_scanner.set_state_callback(scanCbHandler.honor_state_callback)

    scanCbHandler.set_batch_id(BatchType.HONOR, honor_scanner.run_id)

    honor_scanner.start_scan(
        config.scan.kingdom_name, config.scan.people_to_scan, config.scan.formats
    )

    scanCbHandler.honor_scan_finished()


def start_seed_scanner(full_config: str):
    global seed_scanner
    config = FullConfig(**json.loads(full_config))

    seed_scanner = SeedScanner(config.general.adb_port, config)
    seed_scanner.set_batch_callback(scanCbHandler.seed_scan_batch_callback)
    seed_scanner.set_state_callback(scanCbHandler.seed_state_callback)

    scanCbHandler.set_batch_id(BatchType.SEED, seed_scanner.run_id)

    seed_scanner.start_scan(
        config.scan.kingdom_name, config.scan.people_to_scan, config.scan.formats
    )

    scanCbHandler.seed_scan_finished()


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
        global kingdom_confirm_result, kingdomResponse
        kingdom_confirm_result = confirmed
        kingdomResponse.set()
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

    def SaveScanPresets(self, presets: str):
        save_kingdom_presets(TypeAdapter(list[ScanPreset]).validate_json(presets))
        return ""

    def StartBatchScan(self, full_config: str, batchType: str):
        realBatchType = BatchStatus(**json.loads(batchType)).type
        match realBatchType:
            case BatchType.ALLIANCE:
                # Thread(target=start_alliance_scanner, args=(full_config)).start()
                start_alliance_scanner(full_config)
            case BatchType.HONOR:
                start_honor_scanner(full_config)
                pass
            case BatchType.SEED:
                start_seed_scanner(full_config)
                pass
        return ""

    def StopBatchScan(self, batchType: str):
        realBatchType = BatchStatus(**json.loads(batchType)).type
        match realBatchType:
            case BatchType.ALLIANCE:
                alliance_scanner.end_scan()
            case BatchType.HONOR:
                honor_scanner.end_scan()
                pass
            case BatchType.SEED:
                seed_scanner.end_scan()
                pass
        return ""

    # Currently not used
    def ConfirmCallbackBatch(self, confirmed: bool, batchType: str):
        realBatchType = BatchStatus(**json.loads(batchType)).type
        match realBatchType:
            case BatchType.ALLIANCE:
                global alliance_confirm_result, allianceResponse
                alliance_confirm_result = confirmed
                allianceResponse.set()
            case BatchType.HONOR:
                pass
            case BatchType.SEED:
                pass
        return ""


def WebViewApp():
    api = API()
    global window

    if environmentVars.development:
        window = webview.create_window(
            "RoK Tracker Suite - Dev",
            f"http://localhost:{environmentVars.dev_server_port}",
            js_api=api,
            width=1285 + 20,
            height=740 + 40,
        )
    else:
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
