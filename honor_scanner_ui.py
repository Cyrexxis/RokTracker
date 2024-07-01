import logging
import threading
from dummy_root import get_app_root
from roktracker.alliance.additional_data import AdditionalData
from roktracker.alliance.governor_data import GovernorData
from roktracker.honor.scanner import HonorScanner
from roktracker.utils.check_python import check_py_version
from roktracker.utils.exception_handling import GuiExceptionHandler
from roktracker.utils.exceptions import AdbError, ConfigError
from roktracker.utils.general import is_string_int, load_config
from roktracker.utils.gui import InfoDialog
from roktracker.utils.output_formats import OutputFormats

logging.basicConfig(
    filename=str(get_app_root() / "honor-scanner.log"),
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

from dummy_root import get_app_root
from roktracker.utils.validator import sanitize_scanname, validate_installation
from roktracker.utils.adb import get_bluestacks_port
from threading import ExceptHookArgs, Thread
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

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.scan_uuid_label = customtkinter.CTkLabel(self, text="Scan UUID:", height=1)
        self.scan_uuid_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        self.scan_uuid_var = customtkinter.StringVar(self, "---")
        self.scan_uuid_label_2 = customtkinter.CTkLabel(
            self, textvariable=self.scan_uuid_var, height=1, anchor="w"
        )
        self.scan_uuid_label_2.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="ew")

        self.scan_name_label = customtkinter.CTkLabel(self, text="Scan name:", height=1)
        self.scan_name_label.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="w")
        self.scan_name_text = customtkinter.CTkEntry(self)
        self.scan_name_text.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="ew")
        self.scan_name_text.insert(0, config["scan"]["kingdom_name"])

        self.bluestacks_instance_label = customtkinter.CTkLabel(
            self, text="Bluestacks name:", height=1
        )
        self.bluestacks_instance_label.grid(
            row=2, column=0, padx=10, pady=(10, 0), sticky="w"
        )
        self.bluestacks_instance_text = customtkinter.CTkEntry(self)
        self.bluestacks_instance_text.grid(
            row=2, column=1, padx=10, pady=(10, 0), sticky="ew"
        )
        self.bluestacks_instance_text.insert(0, config["general"]["bluestacks"]["name"])

        self.adb_port_label = customtkinter.CTkLabel(self, text="Adb port:", height=1)
        self.adb_port_label.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")
        self.adb_port_text = customtkinter.CTkEntry(
            self,
            validate="all",
            validatecommand=(self.int_validation, "%P", True),
        )
        self.adb_port_text.grid(row=3, column=1, padx=10, pady=(10, 0), sticky="ew")
        self.bluestacks_instance_text.configure(
            validatecommand=(self.register(self.update_port), "%P"), validate="key"
        )
        self.update_port()

        self.scan_amount_label = customtkinter.CTkLabel(
            self, text="People to scan:", height=1
        )
        self.scan_amount_label.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="w")
        self.scan_amount_text = customtkinter.CTkEntry(
            self,
            validate="all",
            validatecommand=(self.int_validation, "%P", True),
        )
        self.scan_amount_text.grid(row=4, column=1, padx=10, pady=(10, 0), sticky="ew")
        self.scan_amount_text.insert(0, str(config["scan"]["people_to_scan"]))

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
            row=5, column=0, padx=10, pady=(5, 0), sticky="ew", columnspan=2
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
            "formats": formats,
        }

    def options_valid(self) -> bool:
        val_errors: List[str] = []

        if not is_string_int(self.adb_port_text.get()):
            val_errors.append("Adb port invalid")

        if not is_string_int(self.scan_amount_text.get()):
            val_errors.append("People to scan invalid")

        if all(value == False for value in self.output_options.get().values()):
            val_errors.append("No output format checked")

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


class AdditionalStatusInfo(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.values: Dict[str, customtkinter.StringVar] = {}
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.gov_number_var = customtkinter.StringVar(value="24 to 30 of 30")
        self.values.update({"govs": self.gov_number_var})
        self.approx_time_remaining_var = customtkinter.StringVar(value="0:16:34")
        self.values.update({"eta": self.approx_time_remaining_var})
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

    def set_var(self, key, value):
        if key in self.values:
            self.values[key].set(value)


class LastBatchInfo(customtkinter.CTkFrame):
    def __init__(self, master, govs_per_batch):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.entries: List[customtkinter.CTkLabel] = []
        self.labels: List[customtkinter.CTkLabel] = []
        self.variables: Dict[str, customtkinter.StringVar] = {}

        self.additional_stats = AdditionalStatusInfo(self)
        self.additional_stats.grid(
            row=0, column=0, columnspan=2, pady=(0, 5), sticky="ewsn"
        )

        offset = 1

        for i in range(0, govs_per_batch):
            label_variable = customtkinter.StringVar(master=self, name=f"name-{i}")
            label = customtkinter.CTkLabel(self, textvariable=label_variable, height=1)
            entry_variable = customtkinter.StringVar(master=self, name=f"score-{i}")
            entry = customtkinter.CTkLabel(self, textvariable=entry_variable, height=1)

            label.grid(
                row=i + offset,  # % ceil(len(values) / 2),
                column=0,
                padx=10,
                pady=2,
                sticky="w",
            )
            entry.grid(
                row=i + offset,  # % ceil(len(values) / 2),
                column=0 + 1,
                padx=(10, 30),
                pady=2,
                sticky="w",
            )

            self.variables.update({f"name-{i}": label_variable})
            self.variables.update({f"score-{i}": entry_variable})
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

        self.title("Honor Scanner by Cyrexxis")
        self.geometry("560x390")
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self.options_frame = BasicOptionsFame(self, self.config)
        self.options_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ewsn")

        self.last_batch_frame = LastBatchInfo(self, 5)

        self.last_batch_frame.set(
            {
                "name-0": "Super Governor 1",
                "score-0": "1000",
                "name-1": "Super Governor 2",
                "score-1": "500",
                "name-2": "Super Governor 3",
                "score-2": "250",
                "name-3": "Super Governor 4",
                "score-3": "125",
                "name-4": "Super Governor 5",
                "score-4": "64",
            }
        )

        self.last_batch_frame.grid(
            row=0, column=1, padx=10, pady=(10, 10), sticky="ewsn", rowspan=2
        )

        self.start_scan_button = customtkinter.CTkButton(
            self, text="Start scan", command=self.start_scan
        )
        self.start_scan_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.end_scan_button = customtkinter.CTkButton(
            self, text="End scan", command=self.end_scan
        )
        self.end_scan_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.current_state = customtkinter.CTkLabel(self, text="Not started", height=1)
        self.current_state.grid(row=2, column=1, padx=10, pady=(10, 0), sticky="ewns")

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
        options = self.options_frame.get_options()

        try:
            self.honor_scanner = HonorScanner(options["port"], self.config)
            self.honor_scanner.set_batch_callback(self.governor_callback)
            self.honor_scanner.set_state_callback(self.state_callback)
            self.options_frame.set_uuid(self.honor_scanner.run_id)

            self.honor_scanner.start_scan(
                options["name"],
                options["amount"],
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
            # Reset end scan button
            self.end_scan_button.configure(state="normal", text="End scan")
            self.start_scan_button.configure(state="normal")

    def end_scan(self):
        self.honor_scanner.end_scan()
        self.end_scan_button.configure(
            state="disabled", text="Abort after next governor"
        )

    def governor_callback(
        self, gov_data: List[GovernorData], extra_data: AdditionalData
    ):
        # self.last_gov_frame.set(gov_info)

        batch_data: Dict[str, str | int] = {}
        for index, gov in enumerate(gov_data):
            batch_data.update({f"name-{index}": gov.name})
            batch_data.update({f"score-{index}": to_int_or(gov.score, "Unknown")})

        batch_data.update(
            {
                "govs": f"{extra_data.current_page * extra_data.govs_per_page} to {(extra_data.current_page + 1) * extra_data.govs_per_page} of {extra_data.target_governor}",
                "time": extra_data.current_time,
                "eta": extra_data.eta(),
            }
        )

        self.last_batch_frame.set(batch_data)

    def state_callback(self, state):
        self.current_state.configure(text=state)


app = App()
app.report_callback_exception = ex_handler.handle_exception
f = open(os.devnull, "w")
sys.stdout = f
sys.stderr = f
app.mainloop()
