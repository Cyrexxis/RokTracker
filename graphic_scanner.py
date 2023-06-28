from math import ceil
from typing import Dict, List, Optional, Tuple, Union
import customtkinter
from rok_scanner import generate_random_id

import customtkinter
import datetime

customtkinter.set_appearance_mode(
    "system"
)  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme(
    "blue"
)  # Themes: "blue" (standard), "green", "dark-blue"


class CheckboxFrame(customtkinter.CTkFrame):
    def __init__(self, master, values):
        super().__init__(master)
        self.values = values
        self.checkboxes: List[customtkinter.CTkCheckBox] = []

        for i, value in enumerate(self.values):
            checkbox = customtkinter.CTkCheckBox(
                self,
                text=value["name"],
                onvalue=True,
                offvalue=False,
                checkbox_height=16,
                checkbox_width=16,
                height=16,
            )
            checkbox.grid(row=i, column=0, padx=10, pady=5, sticky="w")

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
        self.scan_uuid_var = customtkinter.StringVar(self, generate_random_id(8))
        self.scan_uuid_label_2 = customtkinter.CTkLabel(
            self, textvariable=self.scan_uuid_var, height=1, anchor="w"
        )
        self.scan_uuid_label_2.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="ew")

        self.scan_name_label = customtkinter.CTkLabel(self, text="Scan name:", height=1)
        self.scan_name_label.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="w")
        self.scan_name_text = customtkinter.CTkEntry(self)
        self.scan_name_text.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="ew")

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
        self.bluestacks_instance_text.insert(0, "RoK Tracker")

        self.adb_port_label = customtkinter.CTkLabel(self, text="Adb port:", height=1)
        self.adb_port_label.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")
        self.adb_port_text = customtkinter.CTkEntry(self)  # TODO: add validation
        self.adb_port_text.grid(row=3, column=1, padx=10, pady=(10, 0), sticky="ew")
        self.adb_port_text.insert(0, "5555")

        self.scan_amount_label = customtkinter.CTkLabel(
            self, text="People to scan:", height=1
        )
        self.scan_amount_label.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="w")
        self.scan_amount_text = customtkinter.CTkEntry(self)  # TODO: add validation
        self.scan_amount_text.grid(row=4, column=1, padx=10, pady=(10, 0), sticky="ew")
        self.scan_amount_text.insert(0, "600")

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

        self.new_scroll_label = customtkinter.CTkLabel(
            self, text="Advanced scroll:", height=1
        )
        self.new_scroll_label.grid(row=6, column=0, padx=10, pady=(10, 0), sticky="w")
        self.new_scroll_switch = customtkinter.CTkSwitch(
            self, text="", onvalue=True, offvalue=False
        )
        self.new_scroll_switch.grid(row=6, column=1, padx=10, pady=(10, 0), sticky="w")
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

        self.reconstruct_fails_label = customtkinter.CTkLabel(
            self, text="Reconstruct kills:", height=1
        )
        self.reconstruct_fails_label.grid(
            row=8, column=0, padx=10, pady=(10, 0), sticky="w"
        )
        self.reconstruct_fails_switch = customtkinter.CTkSwitch(
            self, text="", onvalue=True, offvalue=False
        )
        self.reconstruct_fails_switch.grid(
            row=8, column=1, padx=10, pady=(10, 0), sticky="w"
        )
        self.reconstruct_fails_switch.select()

    def set_uuid(self, uuid):
        self.scan_uuid_var.set(uuid)

    def get_options(self):
        return {
            "name": self.scan_name_text.get(),
            "port": int(self.adb_port_text.get()),
            "amount": int(self.scan_amount_text.get()),
            "resume": self.resume_scan_checkbox.get(),
            "adv_scroll": self.new_scroll_switch.get(),
            "inactives": self.track_inactives_switch.get(),
            "reconstruct": self.reconstruct_fails_switch.get(),
        }


class CombinedOptionsFrame(customtkinter.CTkFrame):
    def __init__(self, master, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)
        self.values = values
        self.scan_data_options_frame = CheckboxFrame(
            self,
            values,
        )
        self.scan_data_options_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="ewsn"
        )

        self.basic_options = BasicOptionsFame(self)
        self.basic_options.grid(row=0, column=1, padx=10, pady=10, sticky="ewsn")

    def get(self):
        return {
            "to_scan": self.scan_data_options_frame.get(),
            "options": self.basic_options.get_options(),
        }


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

        self.last_time_text = customtkinter.CTkLabel(
            self, textvariable=self.last_time_var, height=1
        )
        self.last_time_text.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.time_remaining_text = customtkinter.CTkLabel(
            self, textvariable=self.approx_time_remaining_var, height=1
        )
        self.time_remaining_text.grid(row=0, column=2, padx=10, pady=5, sticky="e")

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
        self.geometry("760x410")
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self.options_frame = CombinedOptionsFrame(
            self,
            [
                {"name": "T1 Kills", "default": True},
                {"name": "T2 Kills", "default": True},
                {"name": "T3 Kills", "default": True},
                {"name": "T4 Kills", "default": True},
                {"name": "T5 Kills", "default": True},
                {"name": "Ranged", "default": True},
                {"name": "Deads", "default": True},
                {"name": "Rss Assistance", "default": True},
                {"name": "Rss Gathered", "default": True},
                {"name": "Helps", "default": True},
                {"name": "Alliance", "default": True},
            ],
        )
        self.options_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ewsn")

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
            row=0, column=1, padx=10, pady=(10, 10), sticky="ewsn", rowspan=2
        )

        self.start_scan_button = customtkinter.CTkButton(
            self, text="Start scan", command=self.button_callback
        )
        self.start_scan_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    def button_callback(self):
        self.last_gov_frame.set(
            {
                "ID": "12345678",
                "Name": "Super Governor",
                "Power": 100000000,
                "Killpoints": 3000000000,
                "T1 Kills": 343434,
                "T2 Kills": 565656,
                "T3 Kills": 1212121,
                "T4 Kills": 867867868,
                "T5 Kills": 10000000,
                "T4+5 Kills": 10000000,
                "Total Kills": 10000000,
                "Ranged": 200000,
                "Dead": 1000000,
                "Rss Assistance": 9000000000,
                "Helps": 90000,
                "Alliance": "Biggest Alliance ever!",
                "govs": "400 of 900",
                "skipped": "Skipped: 55",
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
                "eta": "01:34:56",
            }
        )

        self.options_frame.basic_options.set_uuid(generate_random_id(8))
        print(self.options_frame.get())
        # print(self.scan_data_options_frame.get())
        pass


app = App()
app.mainloop()
