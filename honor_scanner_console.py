import logging
from dummy_root import get_app_root
from roktracker.utils.check_python import check_py_version

logging.basicConfig(
    filename=str(get_app_root() / "honor-scanner.log"),
    encoding="utf-8",
    format="%(asctime)s %(module)s %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

check_py_version((3, 11))

import json
import questionary
import signal
import sys


from roktracker.alliance.batch_printer import print_batch
from roktracker.honor.scanner import HonorScanner
from roktracker.utils.adb import *
from roktracker.utils.console import console
from roktracker.utils.general import *
from roktracker.utils.ocr import get_supported_langs
from roktracker.utils.validator import validate_installation


logger = logging.getLogger(__name__)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


def ask_abort(honor_scanner: HonorScanner) -> None:
    stop = questionary.confirm(
        message="Do you want to stop the scanner?:", auto_enter=False, default=False
    ).ask()

    if stop:
        console.print("Scan will aborted after next governor.")
        honor_scanner.end_scan()


def main():
    if not validate_installation().success:
        sys.exit(2)

    root_dir = get_app_root()
    config_file = open(root_dir / "config.json")
    config = json.load(config_file)
    config_file.close()

    console.print(
        "Tesseract languages available: "
        + get_supported_langs(str(root_dir / "deps" / "tessdata"))
    )

    try:
        bluestacks_device_name = questionary.text(
            message="Name of your bluestacks instance:",
            default=config["general"]["bluestacks_name"],
        ).unsafe_ask()

        bluestacks_port = int(
            questionary.text(
                f"Adb port of device (detected {get_bluestacks_port(bluestacks_device_name, config)}):",
                default=str(get_bluestacks_port(bluestacks_device_name, config)),
                validate=lambda port: is_string_int(port),
            ).unsafe_ask()
        )

        kingdom = questionary.text(
            message="Kingdom name (used for file name):",
            default=config["scan"]["kingdom_name"],
        ).unsafe_ask()

        scan_amount = int(
            questionary.text(
                message="Number of people to scan:",
                validate=lambda port: is_string_int(port),
                default=str(config["scan"]["people_to_scan"]),
            ).unsafe_ask()
        )
    except:
        console.log("User abort. Exiting scanner.")
        sys.exit(3)

    honor_scanner = HonorScanner(bluestacks_port)
    honor_scanner.set_batch_callback(print_batch)

    console.print(
        f"The UUID of this scan is [green]{honor_scanner.run_id}[/green]",
        highlight=False,
    )
    signal.signal(signal.SIGINT, lambda _, __: ask_abort(honor_scanner))

    honor_scanner.start_scan(kingdom, scan_amount)


if __name__ == "__main__":
    main()
    input("Press enter to exit...")
