import logging
from dummy_root import get_app_root
from roktracker.utils.check_python import check_py_version
from roktracker.utils.exceptions import AdbError, ConfigError
from roktracker.utils.general import (
    is_string_float,
    is_string_int,
    load_config,
    to_int_check,
)
from roktracker.utils.gui import ConfirmDialog, InfoDialog
from roktracker.utils.output_formats import OutputFormats

logging.basicConfig(
    filename=str(get_app_root() / "kingdom-scanner.log"),
    encoding="utf-8",
    format="%(asctime)s %(module)s %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

check_py_version((3, 11))

import customtkinter
import json
import logging
import os
import sys
import threading

from dummy_root import get_app_root
from roktracker.kingdom.additional_data import AdditionalData
from roktracker.kingdom.governor_data import GovernorData
from roktracker.kingdom.scanner import KingdomScanner
from roktracker.utils.adb import get_bluestacks_port
from roktracker.utils.exception_handling import GuiExceptionHandler
from roktracker.utils.validator import validate_installation, sanitize_scanname
from threading import Thread
from typing import Dict, List

logger = logging.getLogger(__name__)
ex_handler = GuiExceptionHandler(logger)

sys.excepthook = ex_handler.handle_exception
threading.excepthook = ex_handler.handle_thread_exception

customtkinter.set_appearance_mode(
    "system"
)  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme(
    "blue"
)  # Themes: "blue" (standard), "green", "dark-blue"


def to_int_or(element, alternative):
    if element == "Skipped":
        return element

    try:
        return int(element)
    except ValueError:
        return alternative


class CheckboxFrame(customtkinter.CTkTabview):
    def __init__(self, master, values, groupName):
        super().__init__(
            master,
            state="disabled",
            width=0,
            height=0,
            segmented_button_fg_color=customtkinter.ThemeManager.theme["CTkFrame"][
                "fg_color"
            ],
            segmented_button_selected_color=customtkinter.ThemeManager.theme[
                "CTkFrame"
            ]["fg_color"],
            text_color_disabled=customtkinter.ThemeManager.theme["CTkLabel"][
                "text_color"
            ],
        )
        self.add(groupName)
        self.values = list(filter(lambda x: x["group"] == groupName, values))  # type: ignore
        self.checkboxes: List[customtkinter.CTkCheckBox] = []

        for i, value in enumerate(self.values):
            checkbox = customtkinter.CTkCheckBox(
                self.tab(groupName),
                text=value["name"],
                onvalue=True,
                offvalue=False,
                checkbox_height=16,
                checkbox_width=16,
                height=16,
            )
            checkbox.grid(row=i, column=0, padx=10, pady=2, sticky="w")

            if value["default"]:
                checkbox.select()

            self.checkboxes.append(checkbox)

    def get(self):
        values = {}
        for checkbox in self.checkboxes:
            values.update({checkbox.cget("text"): checkbox.get()})
        return values


class HorizontalCheckboxFrame(customtkinter.CTkTabview):
    def __init__(self, master, values, groupName, options_per_row):
        super().__init__(
            master,
            state="disabled",
            width=0,
            height=0,
            segmented_button_fg_color=customtkinter.ThemeManager.theme["CTkFrame"][
                "fg_color"
            ],
            segmented_button_selected_color=customtkinter.ThemeManager.theme[
                "CTkFrame"
            ]["fg_color"],
            text_color_disabled=customtkinter.ThemeManager.theme["CTkLabel"][
                "text_color"
            ],
        )
        self.add(groupName)
        self.values = list(filter(lambda x: x["group"] == groupName, values))  # type: ignore
        self.checkboxes: List[Dict[str, customtkinter.CTkCheckBox]] = []

        for i in range(0, options_per_row):
            self.tab(groupName).columnconfigure(i, weight=1)

        cur_row = 0
        for i, value in enumerate(self.values):
            cur_col = i % options_per_row
            label = customtkinter.CTkLabel(
                self.tab(groupName), text=value["name"], height=1
            )
            label.grid(row=cur_row, column=cur_col, padx=10, pady=2)

            checkbox = customtkinter.CTkCheckBox(
                self.tab(groupName),
                text="",
                onvalue=True,
                offvalue=False,
                checkbox_height=20,
                checkbox_width=20,
                height=20,
                width=20,
            )
            checkbox.grid(row=cur_row + 1, column=cur_col, padx=10, pady=2)

            if value["default"]:
                checkbox.select()

            self.checkboxes.append({value["name"]: checkbox})

            if (i + 1) % options_per_row == 0:
                cur_row += 2

    def get(self):
        values = {}
        for checkbox in self.checkboxes:
            for k, v in checkbox.items():
                values.update({k: bool(v.get())})
        return values


class BasicOptionsFame(customtkinter.CTkFrame):
    def __init__(self, master, config):
        super().__init__(master)
        self.config = config

        self.int_validation = self.register(is_string_int)
        self.float_validation = self.register(is_string_float)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.scan_uuid_label = customtkinter.CTkLabel(self, text="Scan UUID:", height=1)
        self.scan_uuid_label.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")
        self.scan_uuid_var = customtkinter.StringVar(self, "---")
        self.scan_uuid_label_2 = customtkinter.CTkLabel(
            self, textvariable=self.scan_uuid_var, height=1, anchor="w"
        )
        self.scan_uuid_label_2.grid(row=0, column=1, padx=10, pady=(5, 0), sticky="ew")

        self.scan_name_label = customtkinter.CTkLabel(self, text="Scan name:", height=1)
        self.scan_name_label.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="w")
        self.scan_name_text = customtkinter.CTkEntry(self)
        self.scan_name_text.grid(row=1, column=1, padx=10, pady=(5, 0), sticky="ew")
        self.scan_name_text.insert(0, config["scan"]["kingdom_name"])

        self.bluestacks_instance_label = customtkinter.CTkLabel(
            self, text="Bluestacks name:", height=1
        )
        self.bluestacks_instance_label.grid(
            row=2, column=0, padx=10, pady=(5, 0), sticky="w"
        )
        self.bluestacks_instance_text = customtkinter.CTkEntry(self)
        self.bluestacks_instance_text.grid(
            row=2, column=1, padx=10, pady=(5, 0), sticky="ew"
        )
        self.bluestacks_instance_text.insert(0, config["general"]["bluestacks"]["name"])

        self.adb_port_label = customtkinter.CTkLabel(self, text="Adb port:", height=1)
        self.adb_port_label.grid(row=3, column=0, padx=10, pady=(5, 0), sticky="w")
        self.adb_port_text = customtkinter.CTkEntry(
            self,
            validate="all",
            validatecommand=(self.int_validation, "%P", True),
        )
        self.adb_port_text.grid(row=3, column=1, padx=10, pady=(5, 0), sticky="ew")
        self.bluestacks_instance_text.configure(
            validatecommand=(self.register(self.update_port), "%P"), validate="key"
        )
        self.update_port()

        self.scan_amount_label = customtkinter.CTkLabel(
            self, text="People to scan:", height=1
        )
        self.scan_amount_label.grid(row=4, column=0, padx=10, pady=(5, 0), sticky="w")
        self.scan_amount_text = customtkinter.CTkEntry(
            self,
            validate="all",
            validatecommand=(self.int_validation, "%P", True),
        )
        self.scan_amount_text.grid(row=4, column=1, padx=10, pady=(5, 0), sticky="ew")
        self.scan_amount_text.insert(0, str(config["scan"]["people_to_scan"]))

        self.resume_scan_label = customtkinter.CTkLabel(
            self, text="Resume scan:", height=1
        )
        self.resume_scan_label.grid(row=5, column=0, padx=10, pady=(5, 0), sticky="w")
        self.resume_scan_checkbox = customtkinter.CTkCheckBox(
            self, text="", onvalue=True, offvalue=False
        )
        self.resume_scan_checkbox.grid(
            row=5, column=1, padx=10, pady=(5, 0), sticky="w"
        )

        if config["scan"]["resume"]:
            self.resume_scan_checkbox.select()

        self.new_scroll_label = customtkinter.CTkLabel(
            self, text="Advanced scroll:", height=1
        )
        self.new_scroll_label.grid(row=6, column=0, padx=10, pady=(5, 0), sticky="w")
        self.new_scroll_switch = customtkinter.CTkSwitch(
            self, text="", onvalue=True, offvalue=False
        )
        self.new_scroll_switch.grid(row=6, column=1, padx=10, pady=(5, 0), sticky="w")

        if config["scan"]["advanced_scroll"]:
            self.new_scroll_switch.select()

        self.track_inactives_label = customtkinter.CTkLabel(
            self, text="Track inactives:", height=1
        )
        self.track_inactives_label.grid(
            row=7, column=0, padx=10, pady=(5, 0), sticky="w"
        )
        self.track_inactives_switch = customtkinter.CTkSwitch(
            self, text="", onvalue=True, offvalue=False
        )
        self.track_inactives_switch.grid(
            row=7, column=1, padx=10, pady=(5, 0), sticky="w"
        )

        if config["scan"]["track_inactives"]:
            self.track_inactives_switch.select()

        self.validate_kills_label = customtkinter.CTkLabel(
            self, text="Validate kills:", height=1
        )
        self.validate_kills_label.grid(
            row=8, column=0, padx=10, pady=(5, 0), sticky="w"
        )
        self.validate_kills_switch = customtkinter.CTkSwitch(
            self, text="", onvalue=True, offvalue=False
        )
        self.validate_kills_switch.grid(
            row=8, column=1, padx=10, pady=(5, 0), sticky="w"
        )

        if config["scan"]["validate_kills"]:
            self.validate_kills_switch.select()

        self.reconstruct_fails_label = customtkinter.CTkLabel(
            self, text="Reconstruct kills:", height=1
        )
        self.reconstruct_fails_label.grid(
            row=9, column=0, padx=10, pady=(5, 0), sticky="w"
        )
        self.reconstruct_fails_switch = customtkinter.CTkSwitch(
            self, text="", onvalue=True, offvalue=False
        )
        self.reconstruct_fails_switch.grid(
            row=9, column=1, padx=10, pady=(5, 0), sticky="w"
        )

        if config["scan"]["reconstruct_kills"]:
            self.reconstruct_fails_switch.select()

        self.validate_power_label = customtkinter.CTkLabel(
            self, text="Validate power:", height=1
        )
        self.validate_power_label.grid(
            row=10, column=0, padx=10, pady=(5, 0), sticky="w"
        )
        self.validate_power_switch = customtkinter.CTkSwitch(
            self, text="", onvalue=True, offvalue=False
        )
        self.validate_power_switch.grid(
            row=10, column=1, padx=10, pady=(5, 0), sticky="w"
        )

        if config["scan"]["validate_power"]:
            self.validate_power_switch.select()

        self.power_threshold_label = customtkinter.CTkLabel(
            self, text="Power tolerance:", height=1
        )
        self.power_threshold_label.grid(
            row=11, column=0, padx=10, pady=(5, 0), sticky="w"
        )
        self.power_threshold_text = customtkinter.CTkEntry(
            self,
            validate="all",
            validatecommand=(self.float_validation, "%P", True),
        )
        self.power_threshold_text.grid(
            row=11, column=1, padx=10, pady=(5, 0), sticky="ew"
        )
        self.power_threshold_text.insert(0, str(config["scan"]["power_threshold"]))

        self.info_close_label = customtkinter.CTkLabel(
            self, text="More info wait:", height=1
        )
        self.info_close_label.grid(row=12, column=0, padx=10, pady=(5, 0), sticky="w")
        self.info_close_text = customtkinter.CTkEntry(
            self,
            validate="all",
            validatecommand=(self.float_validation, "%P", True),
        )
        self.info_close_text.grid(row=12, column=1, padx=10, pady=(5, 0), sticky="ew")
        self.info_close_text.insert(0, str(config["scan"]["timings"]["info_close"]))

        self.gov_close_label = customtkinter.CTkLabel(
            self, text="Governor wait:", height=1
        )
        self.gov_close_label.grid(row=13, column=0, padx=10, pady=(5, 0), sticky="w")
        self.gov_close_text = customtkinter.CTkEntry(
            self,
            validate="all",
            validatecommand=(self.float_validation, "%P", True),
        )
        self.gov_close_text.grid(row=13, column=1, padx=10, pady=(5, 0), sticky="ew")
        self.gov_close_text.insert(0, str(config["scan"]["timings"]["gov_close"]))

        output_values = [
            {
                "name": "xlsx",
                "default": config["scan"]["formats"]["xlsx"],
                "group": "Output Format",
            },
            {
                "name": "csv",
                "default": config["scan"]["formats"]["csv"],
                "group": "Output Format",
            },
            {
                "name": "jsonl",
                "default": config["scan"]["formats"]["jsonl"],
                "group": "Output Format",
            },
        ]
        self.output_options = HorizontalCheckboxFrame(
            self, output_values, "Output Format", 3
        )
        self.output_options.grid(
            row=14, column=0, padx=10, pady=(5, 0), sticky="ew", columnspan=2
        )

    def set_uuid(self, uuid):
        self.scan_uuid_var.set(uuid)

    def update_port(self, name=""):
        self.adb_port_text.delete(0, len(self.adb_port_text.get()))

        if name != "":
            self.adb_port_text.insert(0, get_bluestacks_port(name, self.config))
        else:
            self.adb_port_text.insert(
                0, get_bluestacks_port(self.bluestacks_instance_text.get(), self.config)
            )
        return True

    def get_options(self):
        formats = OutputFormats()
        formats.from_dict(self.output_options.get())
        return {
            "uuid": self.scan_uuid_var.get(),
            "name": self.scan_name_text.get(),
            "port": int(self.adb_port_text.get()),
            "amount": int(self.scan_amount_text.get()),
            "resume": self.resume_scan_checkbox.get(),
            "adv_scroll": self.new_scroll_switch.get(),
            "inactives": self.track_inactives_switch.get(),
            "validate_kills": self.validate_kills_switch.get(),
            "reconstruct": self.reconstruct_fails_switch.get(),
            "validate_power": self.validate_power_switch.get(),
            "power_threshold": self.power_threshold_text.get(),
            "info_time": float(self.info_close_text.get()),
            "gov_time": float(self.gov_close_text.get()),
            "formats": formats,
        }

    def options_valid(self) -> bool:
        val_errors: List[str] = []

        if not is_string_int(self.adb_port_text.get()):
            val_errors.append("Adb port invalid")

        if not is_string_int(self.scan_amount_text.get()):
            val_errors.append("People to scan invalid")

        if not is_string_float(self.info_close_text.get()):
            val_errors.append("Info timing invalid")

        if not is_string_float(self.gov_close_text.get()):
            val_errors.append("Governor timing invalid")

        if (
            not is_string_int(self.power_threshold_text.get())
        ) and self.validate_power_switch.get():
            val_errors.append("Power tolerance invalid")

        if all(value == False for value in self.output_options.get().values()):
            val_errors.append("No output format checked")

        print(self.output_options.get())

        if len(val_errors) > 0:
            InfoDialog(
                "Invalid input",
                "\n".join(val_errors),
                f"200x{100 + len(val_errors) * 12}",
            )

        name_valitation = sanitize_scanname(self.scan_name_text.get())
        if not name_valitation.valid:
            InfoDialog(
                "Name is not valid",
                f"Name is not valid and got changed to:\n{name_valitation.result}\n"
                + f"Please check the new name and press start again.",
                f"400x{100 + 3 * 12}",
            )
            self.scan_name_text.delete(0, customtkinter.END)
            self.scan_name_text.insert(0, name_valitation.result)

        return len(val_errors) == 0 and name_valitation.valid


class ScanOptionsFrame(customtkinter.CTkFrame):
    def __init__(self, master, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.values = values
        self.first_screen_options_frame = CheckboxFrame(self, values, "First Screen")
        self.second_screen_options_frame = CheckboxFrame(self, values, "Second Screen")
        self.third_screen_options_frame = CheckboxFrame(self, values, "Third Screen")

        self.first_screen_options_frame.grid(
            row=0, column=0, padx=10, pady=0, sticky="ewsn"
        )

        self.second_screen_options_frame.grid(
            row=1, column=0, padx=10, pady=0, sticky="ewsn"
        )

        self.third_screen_options_frame.grid(
            row=2, column=0, padx=10, pady=(0, 10), sticky="ewsn"
        )

    def get(self):
        options = {}
        options.update(self.first_screen_options_frame.get())
        options.update(self.second_screen_options_frame.get())
        options.update(self.third_screen_options_frame.get())
        return options


class AdditionalStatusInfo(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.values: Dict[str, customtkinter.StringVar] = {}
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.gov_number_var = customtkinter.StringVar(value="550 of 600")
        self.values.update({"govs": self.gov_number_var})
        self.approx_time_remaining_var = customtkinter.StringVar(value="0:16:34")
        self.values.update({"eta": self.approx_time_remaining_var})
        self.govs_skipped_var = customtkinter.StringVar(value="Skipped: 20")
        self.values.update({"skipped": self.govs_skipped_var})
        self.last_time_var = customtkinter.StringVar(value="13:55:30")
        self.values.update({"time": self.last_time_var})

        self.last_time = customtkinter.CTkLabel(self, text="Current time", height=1)
        self.last_time.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.last_time_text = customtkinter.CTkLabel(
            self, textvariable=self.last_time_var, height=1
        )
        self.last_time_text.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.eta = customtkinter.CTkLabel(self, text="ETA", height=1)
        self.eta.grid(row=0, column=2, padx=10, pady=5, sticky="e")
        self.time_remaining_text = customtkinter.CTkLabel(
            self, textvariable=self.approx_time_remaining_var, height=1
        )
        self.time_remaining_text.grid(row=1, column=2, padx=10, pady=5, sticky="e")

        self.gov_number_text = customtkinter.CTkLabel(
            self, textvariable=self.gov_number_var, height=1
        )
        self.gov_number_text.grid(row=0, column=1, pady=5, sticky="ew")

        self.govs_skipped_text = customtkinter.CTkLabel(
            self, textvariable=self.govs_skipped_var, height=1
        )
        self.govs_skipped_text.grid(row=1, column=1, pady=5)

    def set_var(self, key, value):
        if key in self.values:
            self.values[key].set(value)


class LastGovernorInfo(customtkinter.CTkFrame):
    def __init__(self, master, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.values = values
        self.entries: List[customtkinter.CTkLabel] = []
        self.labels: List[customtkinter.CTkLabel] = []
        self.variables: Dict[str, customtkinter.StringVar] = {}

        self.additional_stats = AdditionalStatusInfo(self)
        self.additional_stats.grid(
            row=0, column=0, columnspan=2, pady=(0, 5), sticky="ewsn"
        )

        offset = 1

        for i, value in enumerate(self.values):
            variable = customtkinter.StringVar(master=self, name=value["name"])
            label = customtkinter.CTkLabel(self, text=value["name"], height=1)
            entry = customtkinter.CTkLabel(self, textvariable=variable, height=1)

            label.grid(
                row=i + offset,  # % ceil(len(values) / 2),
                column=value["col"],
                padx=10,
                pady=2,
                sticky="w",
            )
            entry.grid(
                row=i + offset,  # % ceil(len(values) / 2),
                column=value["col"] + 1,
                padx=(10, 30),
                pady=2,
                sticky="w",
            )

            self.variables.update({value["name"]: variable})
            self.labels.append(label)
            self.entries.append(entry)

        # Additional Info

    def set(self, values):
        for key, value in values.items():
            if key in self.variables:
                if isinstance(value, int):
                    self.variables[key].set(f"{value:,}")
                else:
                    self.variables[key].set(value)
            else:
                self.additional_stats.set_var(key, value)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        file_validation = validate_installation()
        if not file_validation.success:
            self.withdraw()
            dia = InfoDialog(
                "Validation failed",
                "\n".join(file_validation.messages),
                "760x200",
                self.close_program,
            )
            self.wait_window(dia)

        try:
            self.config = load_config()
        except ConfigError as e:
            logger.fatal(str(e))
            dia = InfoDialog(
                "Invalid Config",
                str(e),
                "360x200",
                self.close_program,
            )
            self.wait_window(dia)

        self.title("Kingdom Scanner by Cyrexxis")
        self.geometry("800x590")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=2)
        self.grid_columnconfigure(3, weight=5)
        self.grid_rowconfigure(0, weight=1)

        self.options_frame = BasicOptionsFame(self, self.config)
        self.options_frame.grid(
            row=0, column=1, padx=10, pady=(10, 0), sticky="ewsn", columnspan=2
        )

        self.scan_options_frame = ScanOptionsFrame(
            self,
            [
                {"name": "ID", "default": True, "group": "First Screen"},
                {"name": "Name", "default": True, "group": "First Screen"},
                {"name": "Power", "default": True, "group": "First Screen"},
                {"name": "Killpoints", "default": True, "group": "First Screen"},
                {"name": "Alliance", "default": True, "group": "First Screen"},
                {"name": "T1 Kills", "default": True, "group": "Second Screen"},
                {"name": "T2 Kills", "default": True, "group": "Second Screen"},
                {"name": "T3 Kills", "default": True, "group": "Second Screen"},
                {"name": "T4 Kills", "default": True, "group": "Second Screen"},
                {"name": "T5 Kills", "default": True, "group": "Second Screen"},
                {"name": "Ranged", "default": True, "group": "Second Screen"},
                {"name": "Deads", "default": True, "group": "Third Screen"},
                {"name": "Rss Assistance", "default": True, "group": "Third Screen"},
                {"name": "Rss Gathered", "default": True, "group": "Third Screen"},
                {"name": "Helps", "default": True, "group": "Third Screen"},
            ],
        )
        self.scan_options_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="ewsn", rowspan=2
        )

        self.last_gov_frame = LastGovernorInfo(
            self,
            [
                {"name": "ID", "col": 0},
                {"name": "Name", "col": 0},
                {"name": "Score", "col": 0},
                {"name": "Power", "col": 0},
                {"name": "Killpoints", "col": 0},
                {"name": "T1 Kills", "col": 0},
                {"name": "T2 Kills", "col": 0},
                {"name": "T3 Kills", "col": 0},
                {"name": "T4 Kills", "col": 0},
                {"name": "T5 Kills", "col": 0},
                {"name": "T4+5 Kills", "col": 0},
                {"name": "Total Kills", "col": 0},
                {"name": "Ranged", "col": 0},
                {"name": "Dead", "col": 0},
                {"name": "Rss Assistance", "col": 0},
                {"name": "Rss Gathered", "col": 0},
                {"name": "Helps", "col": 0},
                {"name": "Alliance", "col": 0},
            ],
        )

        self.last_gov_frame.set(
            {
                "ID": "12345678",
                "Name": "Super Governor",
                "Score": "26",
                "Power": 100000000,
                "Killpoints": 3000000000,
                "T1 Kills": 0,
                "T2 Kills": 0,
                "T3 Kills": 0,
                "T4 Kills": 0,
                "T5 Kills": 10000000,
                "T4+5 Kills": 10000000,
                "Total Kills": 10000000,
                "Ranged": 200000,
                "Dead": 1000000,
                "Rss Assistance": 9000000000,
                "Helps": 90000,
                "Alliance": "Biggest Alliance ever!",
            }
        )

        self.last_gov_frame.grid(
            row=0, column=3, padx=10, pady=(10, 10), sticky="ewsn", rowspan=2
        )

        self.start_scan_button = customtkinter.CTkButton(
            self, text="Start scan", command=self.start_scan
        )
        self.start_scan_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.end_scan_button = customtkinter.CTkButton(
            self, text="End scan", command=self.end_scan, state="disabled"
        )
        self.end_scan_button.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        self.current_state = customtkinter.CTkLabel(self, text="Not started", height=1)
        self.current_state.grid(row=1, column=3, padx=10, pady=(10, 0), sticky="ewns")

    def ask_confirm(self, msg) -> bool:
        result = ConfirmDialog("No Governor found", msg, "200x110").get_input()
        self.focus()
        return result

    def close_program(self):
        self.quit()

    def start_scan(self):
        Thread(
            target=self.launch_scanner,
        ).start()

    def launch_scanner(self):
        if not self.options_frame.options_valid():
            return

        self.start_scan_button.configure(state="disabled")
        scan_options = self.scan_options_frame.get()
        options = self.options_frame.get_options()

        self.config["scan"]["timings"]["info_close"] = options["info_time"]
        self.config["scan"]["timings"]["gov_close"] = options["gov_time"]
        self.config["scan"]["advanced_scroll"] = options["adv_scroll"]

        try:
            # Activate end scan button
            self.end_scan_button.configure(state="normal", text="End scan")

            self.kingdom_scanner = KingdomScanner(
                self.config, scan_options, options["port"]
            )
            self.kingdom_scanner.set_governor_callback(self.governor_callback)
            self.kingdom_scanner.set_state_callback(self.state_callback)
            self.kingdom_scanner.set_continue_handler(self.ask_confirm)
            self.options_frame.set_uuid(self.kingdom_scanner.run_id)
            self.kingdom_scanner.start_scan(
                options["name"],
                options["amount"],
                options["resume"],
                options["inactives"],
                options["validate_kills"],
                options["reconstruct"],
                options["validate_power"],
                options["power_threshold"],
                options["formats"],
            )

        except AdbError as error:
            logger.error(
                "An error with the adb connection occured (probably wrong port). Exact message: "
                + str(error)
            )
            InfoDialog(
                "Error",
                "An error with the adb connection occured. Please verfiy that you use the correct port.\nExact message: "
                + str(error),
                "300x160",
            )
            self.state_callback("Not started")

        finally:
            # Reset scan buttons
            self.end_scan_button.configure(state="disabled", text="End scan")
            self.start_scan_button.configure(state="normal")

    def end_scan(self):
        self.kingdom_scanner.end_scan()
        self.end_scan_button.configure(
            state="disabled", text="Abort after next governor"
        )

    def governor_callback(self, gov_data: GovernorData, extra_data: AdditionalData):
        skipped_text = f"{extra_data.skipped_governors} skips"
        if extra_data.skipped_governors == 1:
            skipped_text = f"{extra_data.skipped_governors} skip"

        self.last_gov_frame.set(
            {
                "ID": gov_data.id,
                "Name": gov_data.name,
                "Score": to_int_or(gov_data.score, "Unknown"),
                "Power": to_int_or(gov_data.power, "Unknown"),
                "Killpoints": to_int_or(gov_data.killpoints, "Unknown"),
                "Dead": to_int_or(gov_data.dead, "Unknown"),
                "T1 Kills": to_int_or(gov_data.t1_kills, "Unknown"),
                "T2 Kills": to_int_or(gov_data.t2_kills, "Unknown"),
                "T3 Kills": to_int_or(gov_data.t3_kills, "Unknown"),
                "T4 Kills": to_int_or(gov_data.t4_kills, "Unknown"),
                "T5 Kills": to_int_or(gov_data.t5_kills, "Unknown"),
                "T4+5 Kills": to_int_or(gov_data.t45_kills(), "Unknown"),
                "Total Kills": to_int_or(gov_data.total_kills(), "Unknown"),
                "Ranged": to_int_or(gov_data.ranged_points, "Unknown"),
                "Rss Assistance": to_int_or(gov_data.rss_assistance, "Unknown"),
                "Rss Gathered": to_int_or(gov_data.rss_gathered, "Unknown"),
                "Helps": to_int_or(gov_data.helps, "Unknown"),
                "Alliance": gov_data.alliance,
                "govs": f"{extra_data.current_governor} of {extra_data.target_governor}",
                "skipped": skipped_text,
                "time": extra_data.current_time,
                "eta": extra_data.eta(),
            }
        )

    def state_callback(self, state):
        self.current_state.configure(text=state)


app = App()
app.report_callback_exception = ex_handler.handle_exception
f = open(os.devnull, "w")
sys.stdout = f
sys.stderr = f
app.mainloop()
