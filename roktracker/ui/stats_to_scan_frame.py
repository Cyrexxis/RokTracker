"""Statistics selection frame for the kingdom scanner GUI.

Displays stats grouped by screen type using CheckboxFrame
subcomponents. The get_selection() method computes the current
state and returns it as a dict of CheckboxValue instances."""

from typing import Any

import ttkbootstrap as ttk

from roktracker.ui.checkbox_frames import (
    CheckboxFrame,
    CheckboxGroupValue,
    CheckboxValue,
)


class StatsToScanFrame(ttk.Frame):
    """Frame that shows stats to scan, grouped by screen."""

    def __init__(self, master: Any, values: list[CheckboxGroupValue]):
        """Creates a frame to select what to scan.

        Args:
            master (Any): The ttk widget to use as root
            values (list[CheckboxGroupValue]): The checkbox values to show
        """
        super().__init__(master)
        self.first_screen = CheckboxFrame(self, values, "First Screen")
        self.first_screen.grid(row=0, column=0, sticky="ew")
        self.second_screen = CheckboxFrame(self, values, "Second Screen")
        self.second_screen.grid(row=1, column=0, sticky="ew")
        self.third_screen = CheckboxFrame(self, values, "Third Screen")
        self.third_screen.grid(row=2, column=0, sticky="ew")

    def get_selection(self) -> dict[str, CheckboxValue]:
        """Computes the current state and return it as dict.

        Returns:
            dict[str, CheckboxValue]: Computed result values from all checkboxes
        """
        values: dict[str, CheckboxValue] = {}
        values.update(self.first_screen.get())
        values.update(self.second_screen.get())
        values.update(self.third_screen.get())
        return values
