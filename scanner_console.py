import logging
import signal
import sys
import threading
from typing import Literal

import questionary

from dummy_root import get_app_root
from roktracker.common.config import AppConfig
from roktracker.kingdom.config import KingdomConfig
from roktracker.kingdom.governor_printer import print_gov_state
from roktracker.kingdom.options import STAT_LABELS, KingdomScanOptions, StatsToScan
from roktracker.kingdom.scanner import KingdomScanner
from roktracker.ranking.batch_printer import print_batch
from roktracker.ranking.config import RankingConfig
from roktracker.ranking.options import RankingScanOptions
from roktracker.ranking.scanner import RankingScanner
from roktracker.utils.adb import get_bluestacks_port
from roktracker.utils.console import console
from roktracker.utils.exception_handling import ConsoleExceptionHander
from roktracker.utils.exceptions import AdbError
from roktracker.utils.general import is_string_float, is_string_int
from roktracker.utils.ocr import get_supported_langs
from roktracker.utils.validator import sanitize_scanname, validate_installation

logging.basicConfig(
    filename=str(get_app_root() / "scanner.log"),
    encoding="utf-8",
    format="%(asctime)s %(module)s %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
ex_handler = ConsoleExceptionHander(logger)


sys.excepthook = ex_handler.handle_exception
threading.excepthook = ex_handler.handle_thread_exception


def ask_abort(scanner: KingdomScanner | RankingScanner) -> None:
    stop = questionary.confirm(
        message="Do you want to stop the scanner?:", auto_enter=False, default=False
    ).ask()

    if stop:
        console.print("Scan will aborted after next governor.")
        scanner.end_scan()


def ask_continue(msg: str) -> bool:
    return questionary.confirm(message=msg, auto_enter=False, default=False).ask()


def run_kingdom_scan(config: AppConfig):
    root_dir = get_app_root()
    default_options = KingdomScanOptions.from_json(
        root_dir / "config" / "kingdom_defaults.json"
    )
    options = default_options

    try:
        config.general.bluestacks.name = questionary.text(
            message="Name of your bluestacks instance:",
            default=config.general.bluestacks.name,
        ).unsafe_ask()

        config.general.adb_port = int(
            questionary.text(
                f"Adb port of device (detected {get_bluestacks_port(config)}):",
                default=str(get_bluestacks_port(config)),
                validate=is_string_int,
            ).unsafe_ask()
        )

        options.scan_name = questionary.text(
            message="Kingdom name (used for file name):",
            default=default_options.scan_name,
        ).unsafe_ask()

        validated_name = sanitize_scanname(options.scan_name)
        while not validated_name.valid:
            kingdom = questionary.text(
                message="Kingdom name (Previous name was invalid):",
                default=validated_name.result,
            ).unsafe_ask()
            validated_name = sanitize_scanname(kingdom)

        options.scan_name = validated_name.result

        options.amount = int(
            questionary.text(
                message="Number of people to scan:",
                validate=is_string_int,
                default=str(default_options.amount),
            ).unsafe_ask()
        )

        options.continued = questionary.confirm(
            message="Resume scan:",
            auto_enter=False,
            default=default_options.continued,
        ).unsafe_ask()

        options.advanced_scroll = questionary.confirm(
            message="Use advanced scrolling method:",
            auto_enter=False,
            default=default_options.advanced_scroll,
        ).unsafe_ask()

        options.track_inactives = questionary.confirm(
            message="Screenshot inactives:",
            auto_enter=False,
            default=default_options.track_inactives,
        ).unsafe_ask()

        scan_mode = questionary.select(
            "What scan do you want to do?",
            choices=[
                questionary.Choice(
                    "Full (Everything the scanner can)",
                    value="full",
                    checked=True,
                    shortcut_key="f",
                ),
                questionary.Choice(
                    "Seed (ID, Name, Power, KP, Alliance)",
                    value="seed",
                    checked=False,
                    shortcut_key="s",
                ),
                questionary.Choice(
                    "Custom (select needed items in next step)",
                    value="custom",
                    checked=False,
                    shortcut_key="c",
                ),
            ],
        ).unsafe_ask()

        match scan_mode:
            case "full":
                options.stats_to_scan = StatsToScan()
            case "seed":
                options.stats_to_scan = StatsToScan(
                    id=True,
                    name=True,
                    power=True,
                    killpoints=True,
                    alliance=True,
                    t1_kills=False,
                    t2_kills=False,
                    t3_kills=False,
                    t4_kills=False,
                    t5_kills=False,
                    ranged_points=False,
                    deads=False,
                    assisted=False,
                    gathered=False,
                    helps=False,
                )
            case "custom":
                items_to_scan = questionary.checkbox(
                    "What stats should be scanned?",
                    choices=[
                        questionary.Choice(label, checked=False)
                        for label in STAT_LABELS
                    ],
                ).unsafe_ask()

                if items_to_scan == [] or items_to_scan is None:
                    console.print("Exiting, no items selected.")
                    return

                else:
                    options.stats_to_scan = StatsToScan.nothing()
                    for item in items_to_scan:
                        field_name = STAT_LABELS[item]
                        setattr(options.stats_to_scan, field_name, True)
            case _:
                console.print("Exiting, no mode selected.")
                return

        options.validate_kills = False
        options.reconstruct_kills = False

        if (
            options.stats_to_scan.t1_kills
            and options.stats_to_scan.t2_kills
            and options.stats_to_scan.t3_kills
            and options.stats_to_scan.t4_kills
            and options.stats_to_scan.t5_kills
            and options.stats_to_scan.killpoints
        ):
            options.validate_kills = questionary.confirm(
                message="Validate killpoints:",
                auto_enter=False,
                default=default_options.validate_kills,
            ).unsafe_ask()

        if options.validate_kills:
            options.reconstruct_kills = questionary.confirm(
                message="Try reconstructiong wrong kills values:",
                auto_enter=False,
                default=default_options.reconstruct_kills,
            ).unsafe_ask()

        options.validate_power = questionary.confirm(
            message="Validate power (only works in power ranking):",
            auto_enter=False,
            default=default_options.validate_power,
        ).unsafe_ask()

        options.power_threshold = int(
            questionary.text(
                message="Power threshold to trigger warning:",
                validate=is_string_int,
                default=str(default_options.power_threshold),
            ).unsafe_ask()
        )

        config.timings.info_close = float(
            questionary.text(
                message="Time to wait after more info close:",
                validate=is_string_float,
                default=str(config.timings.info_close),
            ).unsafe_ask()
        )

        config.timings.gov_close = float(
            questionary.text(
                message="Time to wait after governor close:",
                validate=is_string_float,
                default=str(config.timings.gov_close),
            ).unsafe_ask()
        )

        save_formats_tmp = questionary.checkbox(
            "In what format should the result be saved?",
            choices=[
                questionary.Choice(
                    "Excel (xlsx)",
                    value="xlsx",
                    checked=default_options.formats.xlsx,
                ),
                questionary.Choice(
                    "Comma seperated values (csv)",
                    value="csv",
                    checked=default_options.formats.csv,
                ),
                questionary.Choice(
                    "JSON Lines (jsonl)",
                    value="jsonl",
                    checked=default_options.formats.jsonl,
                ),
            ],
        ).unsafe_ask()

        if save_formats_tmp == [] or save_formats_tmp is None:
            console.print("Exiting, no formats selected.")
            return
        else:
            options.formats.from_list(save_formats_tmp)
    except Exception as e:
        logger.error(e)
        sys.exit(-1)
    except KeyboardInterrupt:
        console.log("User abort. Exiting scanner.")
        sys.exit(3)

    try:
        kingdom_scanner = KingdomScanner(
            config,
            KingdomConfig.from_json(root_dir / "config" / "internal" / "kingdom.json"),
        )
        kingdom_scanner.set_continue_handler(ask_continue)
        kingdom_scanner.set_governor_callback(print_gov_state)

        console.print(
            f"The UUID of this scan is [green]{kingdom_scanner.run_id}[/green]",
            highlight=False,
        )

        signal.signal(signal.SIGINT, lambda _, __: ask_abort(kingdom_scanner))

        kingdom_scanner.start_scan(options)
    except AdbError as error:
        logger.error(
            "An error with the adb connection occured (probably wrong port). Exact message: "
            + str(error)
        )
        console.print(
            "An error with the adb connection occured. Please verfiy that you use the correct port.\nExact message: "
            + str(error)
        )


def run_ranking_scan(
    config: AppConfig, scanner_type: Literal["Seed", "Alliance", "Honor"]
):
    root_dir = get_app_root()

    default_options = RankingScanOptions.from_json(
        root_dir / "config" / f"{scanner_type.lower()}_defaults.json"
    )
    options = RankingScanOptions()

    try:
        config.general.bluestacks.name = questionary.text(
            message="Name of your bluestacks instance:",
            default=config.general.bluestacks.name,
        ).unsafe_ask()

        config.general.adb_port = int(
            questionary.text(
                f"Adb port of device (detected {get_bluestacks_port(config)}):",
                default=str(get_bluestacks_port(config)),
                validate=is_string_int,
            ).unsafe_ask()
        )

        options.scan_name = questionary.text(
            message="Scan name:",
            default=default_options.scan_name,
        ).unsafe_ask()

        validated_name = sanitize_scanname(options.scan_name)
        while not validated_name.valid:
            kingdom = questionary.text(
                message="Alliance name (Previous name was invalid):",
                default=validated_name.result,
            ).unsafe_ask()
            validated_name = sanitize_scanname(kingdom)
        options.scan_name = validated_name.result

        options.amount = int(
            questionary.text(
                message="Number of people to scan:",
                validate=is_string_int,
                default=str(default_options.amount),
            ).unsafe_ask()
        )

        save_formats_tmp = questionary.checkbox(
            "In what format should the result be saved?",
            choices=[
                questionary.Choice(
                    "Excel (xlsx)",
                    value="xlsx",
                    checked=default_options.formats.xlsx,
                ),
                questionary.Choice(
                    "Comma seperated values (csv)",
                    value="csv",
                    checked=default_options.formats.csv,
                ),
                questionary.Choice(
                    "JSON Lines (jsonl)",
                    value="jsonl",
                    checked=default_options.formats.jsonl,
                ),
            ],
        ).unsafe_ask()

        if save_formats_tmp == [] or save_formats_tmp is None:
            console.print("Exiting, no formats selected.")
            return
        else:
            options.formats.from_list(save_formats_tmp)
    except Exception as e:
        logger.error(e)
        sys.exit(-1)
    except KeyboardInterrupt:
        console.log("User abort. Exiting scanner.")
        sys.exit(3)

    try:
        scanner = RankingScanner(
            config,
            RankingConfig.from_json(
                root_dir / "config" / "internal" / f"{scanner_type.lower()}.json"
            ),
        )
        scanner.set_batch_callback(print_batch)

        console.print(
            f"The UUID of this scan is [green]{scanner.run_id}[/green]",
            highlight=False,
        )
        signal.signal(signal.SIGINT, lambda _, __: ask_abort(scanner))

        scanner.start_scan(options)
    except AdbError as error:
        logger.error(
            "An error with the adb connection occured (probably wrong port). Exact message: "
            + str(error)
        )
        console.print(
            "An error with the adb connection occured. Please verfiy that you use the correct port.\nExact message: "
            + str(error)
        )


def main():
    if not validate_installation().success:
        sys.exit(2)

    try:
        config = AppConfig()
    except Exception as e:
        logger.fatal(str(e))
        console.log(str(e))
        sys.exit(3)

    console.print(
        "Tesseract languages available: "
        + get_supported_langs(str(get_app_root() / "deps" / "tessdata"))
    )

    try:
        scanner_type: Literal["Kingdom", "Seed", "Alliance", "Honor"] = (
            questionary.select(
                "Select the scanner you want to use:",
                ["Kingdom", "Seed", "Alliance", "Honor"],
                "Kingdom",
            ).unsafe_ask()
        )
    except KeyboardInterrupt:
        console.log("User abort. Exiting scanner.")
        sys.exit(3)

    match scanner_type:
        case "Kingdom":
            run_kingdom_scan(config)
        case _:
            run_ranking_scan(config, scanner_type)


if __name__ == "__main__":
    main()
    input("Press enter to exit...")
