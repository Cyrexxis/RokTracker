from typing import List, Optional, Tuple, Union
import customtkinter
from rok_scanner import generate_random_id

import customtkinter

customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
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
                self, text=value["name"], onvalue=True, offvalue=False
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
        self.scan_name_label = customtkinter.CTkLabel(self, text="Scan name:")
        self.scan_name_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        self.scan_name_text = customtkinter.CTkEntry(self)
        self.scan_name_text.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="w")

        self.bluestacks_instance_label = customtkinter.CTkLabel(
            self, text="Bluestacks name:"
        )
        self.bluestacks_instance_label.grid(
            row=1, column=0, padx=10, pady=(10, 0), sticky="w"
        )
        self.bluestacks_instance_text = customtkinter.CTkEntry(self)
        self.bluestacks_instance_text.grid(
            row=1, column=1, padx=10, pady=(10, 0), sticky="w"
        )
        self.bluestacks_instance_text.insert(0, "RoK Tracker")

        self.adb_port_label = customtkinter.CTkLabel(self, text="Adb port:")
        self.adb_port_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
        self.adb_port_text = customtkinter.CTkEntry(self)  # TODO: add validation
        self.adb_port_text.grid(row=2, column=1, padx=10, pady=(10, 0), sticky="w")

        self.scan_amount_label = customtkinter.CTkLabel(self, text="People to scan:")
        self.scan_amount_label.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")
        self.scan_amount_text = customtkinter.CTkEntry(self)  # TODO: add validation
        self.scan_amount_text.grid(row=3, column=1, padx=10, pady=(10, 0), sticky="w")
        self.scan_amount_text.insert(0, "600")

        self.resume_scan_label = customtkinter.CTkLabel(self, text="Resume scan:")
        self.resume_scan_label.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="w")
        self.resume_scan_checkbox = customtkinter.CTkCheckBox(
            self, text="", onvalue=True, offvalue=False
        )
        self.resume_scan_checkbox.grid(
            row=4, column=1, padx=10, pady=(10, 0), sticky="w"
        )

        self.new_scroll_label = customtkinter.CTkLabel(self, text="Advanced scroll:")
        self.new_scroll_label.grid(row=5, column=0, padx=10, pady=(10, 0), sticky="w")
        self.new_scroll_switch = customtkinter.CTkSwitch(
            self, text="", onvalue=True, offvalue=False
        )
        self.new_scroll_switch.grid(row=5, column=1, padx=10, pady=(10, 0), sticky="w")
        self.new_scroll_switch.select()

        self.track_inactives_label = customtkinter.CTkLabel(
            self, text="Track inactives:"
        )
        self.track_inactives_label.grid(
            row=6, column=0, padx=10, pady=(10, 0), sticky="w"
        )
        self.track_inactives_switch = customtkinter.CTkSwitch(
            self, text="", onvalue=True, offvalue=False
        )
        self.track_inactives_switch.grid(
            row=6, column=1, padx=10, pady=(10, 0), sticky="w"
        )

        self.reconstruct_fails_label = customtkinter.CTkLabel(
            self, text="Advanced scroll:"
        )
        self.reconstruct_fails_label.grid(
            row=7, column=0, padx=10, pady=(10, 0), sticky="w"
        )
        self.reconstruct_fails_switch = customtkinter.CTkSwitch(
            self, text="", onvalue=True, offvalue=False
        )
        self.reconstruct_fails_switch.grid(
            row=7, column=1, padx=10, pady=(10, 0), sticky="w"
        )
        self.reconstruct_fails_switch.select()


class CombinedOptionsFrame(customtkinter.CTkFrame):
    def __init__(self, master, values):
        super().__init__(master)
        self.values = values
        self.scan_data_options_frame = CheckboxFrame(
            self,
            values,
        )
        self.scan_data_options_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="nsw"
        )

        self.basic_options = BasicOptionsFame(self)
        self.basic_options.grid(row=0, column=1, padx=10, pady=10, sticky="nsw")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("RoK Tracker by Cyrexxis")
        self.geometry("500x440")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.options_frame = CombinedOptionsFrame(
            self,
            [
                {"name": "T1 Kills", "default": True},
                {"name": "T2 Kills", "default": True},
                {"name": "T3 Kills", "default": True},
                {"name": "T4 Kills", "default": True},
                {"name": "T5 Kills", "default": True},
                {"name": "Deads", "default": True},
                {"name": "Rss Assistance", "default": True},
                {"name": "Rss Gathered", "default": False},
                {"name": "Helps", "default": True},
                {"name": "Alliance", "default": True},
            ],
        )
        self.options_frame.grid(row=0, column=0, padx=10, pady=(10, 0))

        self.start_scan_button = customtkinter.CTkButton(
            self, text="Start scan", command=self.button_callback
        )
        self.start_scan_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    def button_callback(self):
        # print(self.scan_data_options_frame.get())
        pass


app = App()
app.mainloop()
