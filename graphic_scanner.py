from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
from validator import validate_installation
import customtkinter
import json
import sys
from rok_scanner import (
    generate_random_id,
    start_from_gui,
    end_scan,
    get_bluestacks_port,
)
from threading import Thread

if not validate_installation():
    exit(2)

if getattr(sys, "frozen", False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    print("Bundle detected!")
    root_dir = Path(sys.executable).parent
else:
    root_dir = Path(__file__).parent

config_file = open(root_dir / "config.json")
config = json.load(config_file)
config_file.close()

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
        self.values = list(filter(lambda x: x["group"] == groupName, values))
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


class BasicOptionsFame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
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
        self.bluestacks_instance_text.insert(0, config["general"]["bluestacks_name"])

        self.adb_port_label = customtkinter.CTkLabel(self, text="Adb port:", height=1)
        self.adb_port_label.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")
        self.adb_port_text = customtkinter.CTkEntry(self)  # TODO: add validation
        self.adb_port_text.grid(row=3, column=1, padx=10, pady=(10, 0), sticky="ew")
        self.bluestacks_instance_text.configure(
            validatecommand=(self.register(self.update_port), "%P"), validate="key"
        )
        self.update_port()

        self.scan_amount_label = customtkinter.CTkLabel(
            self, text="People to scan:", height=1
        )
        self.scan_amount_label.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="w")
        self.scan_amount_text = customtkinter.CTkEntry(self)  # TODO: add validation
        self.scan_amount_text.grid(row=4, column=1, padx=10, pady=(10, 0), sticky="ew")
        self.scan_amount_text.insert(0, str(config["scan"]["people_to_scan"]))

        self.resume_scan_label = customtkinter.CTkLabel(
            self, text="Resume scan:", height=1
        )
        self.resume_scan_label.grid(row=5, column=0, padx=10, pady=(10, 0), sticky="w")
        self.resume_scan_checkbox = customtkinter.CTkCheckBox(
            self, text="", onvalue=True, offvalue=False
        )
        self.resume_scan_checkbox.grid(
            row=5, column=1, padx=10, pady=(10, 0), sticky="w"
        )

        if config["scan"]["resume"]:
            self.resume_scan_checkbox.select()

        self.new_scroll_label = customtkinter.CTkLabel(
            self, text="Advanced scroll:", height=1
        )
        self.new_scroll_label.grid(row=6, column=0, padx=10, pady=(10, 0), sticky="w")
        self.new_scroll_switch = customtkinter.CTkSwitch(
            self, text="", onvalue=True, offvalue=False
        )
        self.new_scroll_switch.grid(row=6, column=1, padx=10, pady=(10, 0), sticky="w")

        if config["scan"]["advanced_scroll"]:
            self.new_scroll_switch.select()

        self.track_inactives_label = customtkinter.CTkLabel(
            self, text="Track inactives:", height=1
        )
        self.track_inactives_label.grid(
            row=7, column=0, padx=10, pady=(10, 0), sticky="w"
        )
        self.track_inactives_switch = customtkinter.CTkSwitch(
            self, text="", onvalue=True, offvalue=False
        )
        self.track_inactives_switch.grid(
            row=7, column=1, padx=10, pady=(10, 0), sticky="w"
        )

        if config["scan"]["track_inactives"]:
            self.track_inactives_switch.select()

        self.validate_kills_label = customtkinter.CTkLabel(
            self, text="Validate kills:", height=1
        )
        self.validate_kills_label.grid(
            row=8, column=0, padx=10, pady=(10, 0), sticky="w"
        )
        self.validate_kills_switch = customtkinter.CTkSwitch(
            self, text="", onvalue=True, offvalue=False
        )
        self.validate_kills_switch.grid(
            row=8, column=1, padx=10, pady=(10, 0), sticky="w"
        )

        if config["scan"]["validate_kills"]:
            self.validate_kills_switch.select()

        self.reconstruct_fails_label = customtkinter.CTkLabel(
            self, text="Reconstruct kills:", height=1
        )
        self.reconstruct_fails_label.grid(
            row=9, column=0, padx=10, pady=(10, 0), sticky="w"
        )
        self.reconstruct_fails_switch = customtkinter.CTkSwitch(
            self, text="", onvalue=True, offvalue=False
        )
        self.reconstruct_fails_switch.grid(
            row=9, column=1, padx=10, pady=(10, 0), sticky="w"
        )

        if config["scan"]["reconstruct_kills"]:
            self.reconstruct_fails_switch.select()

        self.info_close_label = customtkinter.CTkLabel(
            self, text="More info wait:", height=1
        )
        self.info_close_label.grid(row=10, column=0, padx=10, pady=(10, 0), sticky="w")
        self.info_close_text = customtkinter.CTkEntry(self)  # TODO: add validation
        self.info_close_text.grid(row=10, column=1, padx=10, pady=(10, 0), sticky="ew")
        self.info_close_text.insert(0, str(config["scan"]["timings"]["info_close"]))

        self.gov_close_label = customtkinter.CTkLabel(
            self, text="Governor wait:", height=1
        )
        self.gov_close_label.grid(row=11, column=0, padx=10, pady=(10, 0), sticky="w")
        self.gov_close_text = customtkinter.CTkEntry(self)  # TODO: add validation
        self.gov_close_text.grid(row=11, column=1, padx=10, pady=(10, 0), sticky="ew")
        self.gov_close_text.insert(0, str(config["scan"]["timings"]["gov_close"]))

    def set_uuid(self, uuid):
        self.scan_uuid_var.set(uuid)

    def update_port(self, name=""):
        self.adb_port_text.delete(0, len(self.adb_port_text.get()))

        if name != "":
            self.adb_port_text.insert(0, get_bluestacks_port(name))
        else:
            self.adb_port_text.insert(
                0, get_bluestacks_port(self.bluestacks_instance_text.get())
            )
        return True

    def get_options(self):
        return {
            "uuid": self.scan_uuid_var.get(),
            "name": self.scan_name_text.get(),
            "port": int(self.adb_port_text.get()),
            "amount": int(self.scan_amount_text.get()),
            "resume": self.resume_scan_checkbox.get(),
            "adv_scroll": self.new_scroll_switch.get(),
            "inactives": self.track_inactives_switch.get(),
            "validate": self.validate_kills_switch.get(),
            "reconstruct": self.reconstruct_fails_switch.get(),
            "info_time": float(self.info_close_text.get()),
            "gov_time": float(self.gov_close_text.get()),
        }


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

        self.title("RoK Tracker by Cyrexxis")
        self.geometry("760x535")
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self.options_frame = BasicOptionsFame(
            self,
        )
        self.options_frame.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="ewsn")

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
            row=0, column=0, padx=10, pady=10, sticky="ewsn", rowspan=3
        )

        self.last_gov_frame = LastGovernorInfo(
            self,
            [
                {"name": "ID", "col": 0},
                {"name": "Name", "col": 0},
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
            row=0, column=2, padx=10, pady=(10, 10), sticky="ewsn", rowspan=2
        )

        self.start_scan_button = customtkinter.CTkButton(
            self, text="Start scan", command=self.start_scan
        )
        self.start_scan_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.end_scan_button = customtkinter.CTkButton(
            self, text="End scan", command=self.end_scan
        )
        self.end_scan_button.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        self.current_state = customtkinter.CTkLabel(self, text="Not started", height=1)
        self.current_state.grid(row=2, column=2, padx=10, pady=(10, 0), sticky="ewns")

    def start_scan(self):
        self.options_frame.set_uuid(generate_random_id(8))
        options = self.options_frame.get_options()
        scan_options = self.scan_options_frame.get()
        Thread(
            target=start_from_gui,
            args=(options, scan_options, self.governor_callback, self.state_callback),
        ).start()

    def end_scan(self):
        end_scan()

    def governor_callback(self, gov_info):
        # self.last_gov_frame.set(gov_info)
        self.last_gov_frame.set(
            {
                "ID": gov_info["id"],
                "Name": gov_info["name"],
                "Power": to_int_or(gov_info["power"], "Unknown"),
                "Killpoints": to_int_or(gov_info["killpoints"], "Unknown"),
                "Dead": to_int_or(gov_info["dead"], "Unknown"),
                "T1 Kills": to_int_or(gov_info["kills_t1"], "Unknown"),
                "T2 Kills": to_int_or(gov_info["kills_t2"], "Unknown"),
                "T3 Kills": to_int_or(gov_info["kills_t3"], "Unknown"),
                "T4 Kills": to_int_or(gov_info["kills_t4"], "Unknown"),
                "T5 Kills": to_int_or(gov_info["kills_t5"], "Unknown"),
                "T4+5 Kills": to_int_or(gov_info["kills_t45"], "Unknown"),
                "Total Kills": to_int_or(gov_info["kills_total"], "Unknown"),
                "Ranged": to_int_or(gov_info["ranged_points"], "Unknown"),
                "Rss Assistance": to_int_or(gov_info["rss_assistance"], "Unknown"),
                "Rss Gathered": to_int_or(gov_info["rss_gathered"], "Unknown"),
                "Helps": to_int_or(gov_info["helps"], "Unknown"),
                "Alliance": gov_info["alliance"].rstrip(),
                "govs": gov_info["govs"],
                "skipped": gov_info["skipped"],
                "time": gov_info["time"],
                "eta": gov_info["eta"],
            }
        )

    def state_callback(self, state):
        self.current_state.configure(text=state)


app = App()
app.mainloop()
