from typing import Any

import ttkbootstrap as ttk

from roktracker.ui.checkbox_frames import (
    CheckboxFrame,
    CheckboxGroupValue,
    CheckboxValue,
)


class StatsToScanFrame(ttk.Frame):
    def __init__(self, master: Any, values: list[CheckboxGroupValue]):
        super().__init__(master)
        self.first_screen = CheckboxFrame(self, values, "First Screen")
        self.first_screen.grid(row=0, column=0, sticky="ew")
        self.second_screen = CheckboxFrame(self, values, "Second Screen")
        self.second_screen.grid(row=1, column=0, sticky="ew")
        self.third_screen = CheckboxFrame(self, values, "Third Screen")
        self.third_screen.grid(row=2, column=0, sticky="ew")

    def get_selection(self) -> dict[str, CheckboxValue]:
        values: dict[str, CheckboxValue] = {}
        values.update(self.first_screen.get())
        values.update(self.second_screen.get())
        values.update(self.third_screen.get())
        return values
