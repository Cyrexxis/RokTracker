from typing import List
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
                self, text=value, onvalue=True, offvalue=False
            )
            checkbox.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="w")
            self.checkboxes.append(checkbox)

    def get(self):
        values = {}
        for checkbox in self.checkboxes:
            values.update({checkbox.cget("text"): checkbox.get()})
        return values


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("RoK Tracker by Cyrexxis")
        self.geometry("400x410")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scan_data_options_frame = CheckboxFrame(
            self,
            [
                "T1 Kills",
                "T2 Kills",
                "T3 Kills",
                "T4 Kills",
                "T5 Kills",
                "Deads",
                "Rss Assistance",
                "Rss Gathered",
                "Helps",
                "Alliance",
            ],
        )
        self.scan_data_options_frame.grid(
            row=0, column=0, padx=10, pady=(10, 0), sticky="nsw"
        )

        self.button = customtkinter.CTkButton(
            self, text="my button", command=self.button_callback
        )
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

    def button_callback(self):
        print(self.scan_data_options_frame.get())


app = App()
app.mainloop()
