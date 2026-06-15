"""GUI for the ranking scanner workflow.

Provides the RankingScannerUI class that assembles all UI
components and wires them to the RankingScanner. Handles
validation and launch in a background thread."""

import logging
from threading import Thread
from typing import Any

import ttkbootstrap as ttk

from dummy_root import get_app_root
from roktracker.common.config import AppConfig
from roktracker.common.data import AdditionalScanData
from roktracker.ranking.config import RankingConfig
from roktracker.ranking.options import RankingScanOptions
from roktracker.ranking.ranking_data import RankingData
from roktracker.ranking.scanner import RankingScanner
from roktracker.ui.checkbox_frames import (
    HorizontalCheckboxFrame,
)
from roktracker.ui.options_frame import OptionsElement, OptionsFrame
from roktracker.ui.placeholders import (
    ADDITIONAL_RANKING_STATS_PLACEHOLDER,
    RANKING_STATS_PLACEHOLDER,
)
from roktracker.ui.status_frame import StatusInfoFrame
from roktracker.ui.utils import (
    additional_batch_data_to_info,
    batch_to_info,
    formats_to_checkbox,
    ro_to_options,
    show_error,
    update_config_option,
    update_config_options,
)
from roktracker.utils.exceptions import AdbError
from roktracker.utils.validator import sanitize_scan_name

logger = logging.getLogger(__name__)


class RankingScannerUI(ttk.Frame):
    """The complete GUI of the ranking scanner."""

    def __init__(
        self,
        master: Any,
        app_config: AppConfig,
    ):
        """Creates a ranking scanner frame.

        Args:
            master (Any): The ttk widget to use as root
            app_config (AppConfig): The AppConfig to use
        """
        super().__init__(master)

        self.root_dir = get_app_root()
        self.scanner_type: str = "Alliance"
        self.default_options = RankingScanOptions.from_json(
            self.root_dir / "config" / f"{self.scanner_type.lower()}_defaults.json"
        )
        self.selected_options = RankingScanOptions()
        self.app_config = app_config

        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        combobox_frame = ttk.Frame(self)
        combobox_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ewsn")
        combobox_frame.grid_columnconfigure(0, weight=1)
        combobox_frame.grid_columnconfigure(1, weight=2)

        mode_selection_label = ttk.Label(combobox_frame, text="Mode")
        mode_selection_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ewsn")

        self.selected_mode = ttk.StringVar(self, "Alliance")
        self.mode_selection = ttk.Combobox(
            combobox_frame,
            values=["Alliance", "Seed", "Honor"],
            textvariable=self.selected_mode,
            state="readonly",
        )
        self.mode_selection.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="ewsn")

        self.scan_options = OptionsFrame(
            self, ro_to_options(self.app_config, self.default_options)
        )
        self.scan_options.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="ewsn")

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
            "ranking_status",
            RANKING_STATS_PLACEHOLDER,
            ADDITIONAL_RANKING_STATS_PLACEHOLDER,
        )
        self.status_frame.grid(
            row=0, column=1, padx=10, pady=(10, 10), sticky="ewsn", rowspan=4
        )

        control_frame = ttk.Frame(self)
        control_frame.grid(row=2, column=0, columnspan=2, pady=(5, 0), sticky="ew")
        control_frame.grid_columnconfigure(2, weight=1)

        self.start_button = ttk.Button(
            control_frame, text="Start scan", command=self.start_scan
        )
        self.start_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.stop_button = ttk.Button(
            control_frame, text="Stop scan", command=self.stop_scan, state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.current_state = ttk.Label(control_frame, text="Not started")
        self.current_state.grid(row=0, column=3, padx=10, pady=(10, 0), sticky="ewsn")

    def start_scan(self):
        """Validates the input and starts the scanner in a new thread."""
        options = self.scan_options.get_options()
        update_config_options(self.selected_options, options)
        name_validation = sanitize_scan_name(self.selected_options.scan_name)
        if not name_validation.valid:
            show_error(
                self,
                f"Name is not valid and got changed to:\n{name_validation.result}\n"
                + "Please check the new name and press start again.",
                "Name is not valid",
            )

            self.scan_options.set_option(
                OptionsElement(
                    name="scan_name",
                    display_name="Scan Name",
                    value=name_validation.result,
                )
            )
            return

        Thread(target=self.launch_scanner).start()

    def launch_scanner(self):
        """Evaluates the selected options and starts the scan."""
        self.start_button.config(state="disabled")

        self.scanner_type = self.selected_mode.get()
        options = self.scan_options.get_options()
        options.update(OptionsElement.from_checkboxes(self.output_format_options.get()))

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

            self.ranking_scanner = RankingScanner(
                self.app_config,
                RankingConfig.from_json(
                    self.root_dir
                    / "config"
                    / "internal"
                    / f"{self.scanner_type.lower()}.json"
                ),
            )

            self.ranking_scanner.set_batch_callback(self.batch_callback)
            self.ranking_scanner.set_state_callback(self.state_callback)
            self.scan_options.set_option(
                OptionsElement(
                    name="scan_uuid",
                    display_name="Scan UUID",
                    value=self.ranking_scanner.run_id,
                    editable=False,
                )
            )

            update_config_options(
                self.selected_options.formats,
                OptionsElement.from_checkboxes(formats_to_use),
            )

            update_config_options(self.selected_options, options)

            self.ranking_scanner.start_scan(self.selected_options)

        except AdbError as error:
            logger.error(
                "An error with the adb connection occurred (probably wrong port). Exact message: "
                + str(error)
            )

            show_error(
                parent=self,
                message="An error with the adb connection occurred. Please verify that you use the correct port.\nExact message: "
                + str(error),
                title="ADB Error",
            )

            self.state_callback("Not started")

        finally:
            # Reset scan buttons
            self.stop_button.configure(state="disabled", text="End scan")
            self.start_button.configure(state="normal")

    def stop_scan(self):
        """Stops the scan after the current batch."""
        self.ranking_scanner.end_scan()
        self.stop_button.configure(state="disabled", text="Abort after next batch")

    def batch_callback(
        self, ranking: list[RankingData], additional: AdditionalScanData
    ):
        """Handles the display of the last scanned batch.

        Args:
            ranking (list[RankingData]): Batch related data
            additional (AdditionalScanData): Scan related data
        """
        self.status_frame.update_status(
            batch_to_info(ranking), additional_batch_data_to_info(additional)
        )

    def state_callback(self, state: str):
        """Updates the state text.

        Args:
            state (str): New state to display
        """
        self.current_state.configure(text=state)
