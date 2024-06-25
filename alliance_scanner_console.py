import logging
import threading
from dummy_root import get_app_root
from roktracker.utils.check_python import check_py_version
from roktracker.utils.exception_handling import ConsoleExceptionHander
from roktracker.utils.output_formats import OutputFormats

logging.basicConfig(
    filename=str(get_app_root() / "alliance-scanner.log"),
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
from roktracker.alliance.scanner import AllianceScanner
from roktracker.utils.adb import *
from roktracker.utils.console import console
from roktracker.utils.general import *
from roktracker.utils.ocr import get_supported_langs
from roktracker.utils.validator import sanitize_scanname, validate_installation


logger = logging.getLogger(__name__)
ex_handler = ConsoleExceptionHander(logger)


sys.excepthook = ex_handler.handle_exception
threading.excepthook = ex_handler.handle_thread_exception


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


def ask_abort(alliance_scanner: AllianceScanner) -> None:
    stop = questionary.confirm(
        message="Do you want to stop the scanner?:", auto_enter=False, default=False
    ).ask()

    if stop:
        console.print("Scan will aborted after next governor.")
        alliance_scanner.end_scan()


def main():
    if not validate_installation().success:
        sys.exit(2)

    root_dir = get_app_root()

    try:
        config = load_config()
    except ConfigError as e:
        logger.fatal(str(e))
        console.log(str(e))
        sys.exit(3)

    console.print(
        "Tesseract languages available: "
        + get_supported_langs(str(root_dir / "deps" / "tessdata"))
    )

    try:
        bluestacks_device_name = questionary.text(
            message="Name of your bluestacks instance:",
            default=config["general"]["bluestacks"]["name"],
        ).unsafe_ask()

        bluestacks_port = int(
            questionary.text(
                f"Adb port of device (detected {get_bluestacks_port(bluestacks_device_name, config)}):",
                default=str(get_bluestacks_port(bluestacks_device_name, config)),
                validate=lambda port: is_string_int(port),
            ).unsafe_ask()
        )

        kingdom = questionary.text(
            message="Alliance name (used for file name):",
            default=config["scan"]["kingdom_name"],
        ).unsafe_ask()

        validated_name = sanitize_scanname(kingdom)
        while not validated_name.valid:
            kingdom = questionary.text(
                message="Alliance name (Previous name was invalid):",
                default=validated_name.result,
            ).unsafe_ask()
            validated_name = sanitize_scanname(kingdom)

        scan_amount = int(
            questionary.text(
                message="Number of people to scan:",
                validate=lambda port: is_string_int(port),
                default=str(config["scan"]["people_to_scan"]),
            ).unsafe_ask()
        )

        save_formats = OutputFormats()
        save_formats_tmp = questionary.checkbox(
            "In what format should the result be saved?",
            choices=[
                questionary.Choice(
                    "Excel (xlsx)",
                    value="xlsx",
                    checked=config["scan"]["formats"]["xlsx"],
                ),
                questionary.Choice(
                    "Comma seperated values (csv)",
                    value="csv",
                    checked=config["scan"]["formats"]["csv"],
                ),
                questionary.Choice(
                    "JSON Lines (jsonl)",
                    value="jsonl",
                    checked=config["scan"]["formats"]["jsonl"],
                ),
            ],
        ).unsafe_ask()

        if save_formats_tmp == [] or save_formats_tmp == None:
            console.print("Exiting, no formats selected.")
            return
        else:
            save_formats.from_list(save_formats_tmp)
    except:
        console.log("User abort. Exiting scanner.")
        sys.exit(3)

    try:
        alliance_scanner = AllianceScanner(bluestacks_port, config)
        alliance_scanner.set_batch_callback(print_batch)

        console.print(
            f"The UUID of this scan is [green]{alliance_scanner.run_id}[/green]",
            highlight=False,
        )
        signal.signal(signal.SIGINT, lambda _, __: ask_abort(alliance_scanner))

        alliance_scanner.start_scan(kingdom, scan_amount, save_formats)
    except AdbError as error:
        logger.error(
            "An error with the adb connection occured (probably wrong port). Exact message: "
            + str(error)
        )
        console.print(
            "An error with the adb connection occured. Please verfiy that you use the correct port.\nExact message: "
            + str(error)
        )


if __name__ == "__main__":
    main()
    input("Press enter to exit...")
