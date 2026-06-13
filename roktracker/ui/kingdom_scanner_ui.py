import logging
from threading import Thread
from typing import Any

import ttkbootstrap as ttk

from dummy_root import get_app_root
from roktracker.common.config import AppConfig
from roktracker.kingdom.config import KingdomConfig
from roktracker.kingdom.governor_data import AdditionalGovernorData, GovernorData
from roktracker.kingdom.options import KingdomScanOptions
from roktracker.kingdom.scanner import KingdomScanner
from roktracker.ui.checkbox_frames import (
    HorizontalCheckboxFrame,
)
from roktracker.ui.options_frame import OptionsElement, OptionsFrame
from roktracker.ui.placeholders import (
    additional_stats_placeholder,
    kingdom_stats_placeholder,
)
from roktracker.ui.stats_to_scan_frame import StatsToScanFrame
from roktracker.ui.status_frame import StatusInfoFrame
from roktracker.ui.utils import (
    additional_data_to_info,
    formats_to_checkbox,
    governor_to_info,
    ko_to_options,
    show_confirm,
    show_error,
    sts_to_checkbox,
    update_config_option,
    update_config_options,
)
from roktracker.utils.exceptions import AdbError

logger = logging.getLogger(__name__)


class KingdomScannerUI(ttk.Frame):
    def __init__(self, master: Any, app_config: AppConfig):
        super().__init__(master)

        self.root_dir = get_app_root()
        self.default_options = KingdomScanOptions.from_json(
            self.root_dir / "config" / "kingdom_defaults.json"
        )
        self.selected_options = KingdomScanOptions()
        self.app_config = app_config

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=2)
        self.grid_columnconfigure(3, weight=5)
        self.grid_rowconfigure(0, weight=1)

        self.stats_to_scan_frame = StatsToScanFrame(
            self, sts_to_checkbox(self.default_options.stats_to_scan)
        )
        self.stats_to_scan_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="ewsn", rowspan=2
        )

        self.scan_options = OptionsFrame(
            self, ko_to_options(self.app_config, self.default_options)
        )
        self.scan_options.grid(
            row=0, column=1, padx=10, pady=(10, 0), sticky="ewsn", columnspan=2
        )

        self.output_format_options = HorizontalCheckboxFrame(
            self.scan_options,
            formats_to_checkbox(self.default_options.formats),
            "Output Format",
        )
        (options_cols, options_rows) = self.scan_options.grid_size()
        self.output_format_options.grid(
            row=options_rows,
            column=0,
            pady=(5, 0),
            sticky="ew",
            columnspan=options_cols,
        )

        self.status_frame = StatusInfoFrame(
            self,
            "kingdom_status",
            kingdom_stats_placeholder,
            additional_stats_placeholder,
        )
        self.status_frame.grid(row=0, column=3, padx=10, pady=(10, 0), sticky="ewsn")

        controll_frame = ttk.Frame(self)
        controll_frame.grid(row=1, column=0, columnspan=4, pady=(5, 0), sticky="ew")
        controll_frame.grid_columnconfigure(2, weight=1)

        self.start_button = ttk.Button(
            controll_frame, text="Start scan", command=self.start_scan
        )
        self.start_button.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.stop_button = ttk.Button(
            controll_frame, text="Stop scan", command=self.stop_scan, state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=10, pady=(0, 10), sticky="ew")

        self.current_state = ttk.Label(controll_frame, text="Not started")
        self.current_state.grid(row=0, column=3, padx=10, pady=(0, 10), sticky="ewns")

    def ask_confirm(self, msg: str) -> bool:
        return show_confirm(self, msg, "No Governor found")

    def start_scan(self):
        Thread(target=self.launch_scanner).start()

    def launch_scanner(self):
        self.start_button.config(state="disabled")

        options = self.scan_options.get_options()
        options.update(OptionsElement.from_checkboxes(self.output_format_options.get()))

        stats_to_scan = self.stats_to_scan_frame.get_selection()
        formats_to_use = self.output_format_options.get()

        update_config_option(
            self.app_config.general.bluestacks, options.get("info_close")
        )
        update_config_option(
            self.app_config.general.bluestacks, options.get("gov_close")
        )
        update_config_option(self.app_config.general, options.get("adb_port"))

        try:
            self.stop_button.configure(state="normal", text="End scan")

            self.kingdom_scanner = KingdomScanner(
                self.app_config,
                KingdomConfig.from_json(
                    self.root_dir / "config" / "internal" / "kingdom.json"
                ),
            )

            self.kingdom_scanner.set_governor_callback(self.governor_callback)
            self.kingdom_scanner.set_state_callback(self.state_callback)
            self.kingdom_scanner.set_continue_handler(self.ask_confirm)
            self.scan_options.set_option(
                OptionsElement(
                    name="scan_uuid",
                    display_name="Scan UUID",
                    value=self.kingdom_scanner.run_id,
                    editable=False,
                )
            )

            update_config_options(
                self.selected_options.stats_to_scan,
                OptionsElement.from_checkboxes(stats_to_scan),
            )

            update_config_options(
                self.selected_options.formats,
                OptionsElement.from_checkboxes(formats_to_use),
            )

            update_config_options(self.selected_options, options)

            self.kingdom_scanner.start_scan(self.selected_options)

        except AdbError as error:
            logger.error(
                "An error with the adb connection occured (probably wrong port). Exact message: "
                + str(error)
            )

            show_error(
                parent=self,
                message="An error with the adb connection occured. Please verfiy that you use the correct port.\nExact message: "
                + str(error),
                title="ADB Error",
            )

            self.state_callback("Not started")

        finally:
            # Reset scan buttons
            self.stop_button.configure(state="disabled", text="End scan")
            self.start_button.configure(state="normal")

    def stop_scan(self):
        self.kingdom_scanner.end_scan()
        self.stop_button.configure(state="disabled", text="Abort after next governor")

    def governor_callback(
        self, governor: GovernorData, additional: AdditionalGovernorData
    ):
        self.status_frame.update_status(
            governor_to_info(governor), additional_data_to_info(additional)
        )

    def state_callback(self, state: str):
        self.current_state.configure(text=state)
