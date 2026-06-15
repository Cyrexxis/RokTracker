"""GUI components for checkbox input in ttkbootstrap applications.

Provides CheckboxFrame (vertical layout) and HorizontalCheckboxFrame
for displaying grouped checkbox options. Exports the CheckboxGroupValue,
CheckboxRawValue, and CheckboxValue data classes."""

from dataclasses import dataclass
from typing import Any

import ttkbootstrap as ttk


@dataclass
class CheckboxGroupValue:
    """The input for a CheckboxFrame.

    Attributes:
        name (str): The internal name
        display_name (str): The displayed name
        group (str): The group the entry belongs to
        default (bool): The default value
    """

    name: str
    display_name: str
    group: str
    default: bool


@dataclass
class CheckboxRawValue:
    """Raw version of a checkbox value.

    Attributes:
        name (str): The internal name
        display_name (str): The displayed name
        value (ttk.BooleanVar): The ttk variable that stores the data
    """

    name: str
    display_name: str
    value: ttk.BooleanVar


@dataclass
class CheckboxValue:
    """The return value of a CheckboxFrame.

    Attributes:
        name (str): The internal name
        display_name (str): The displayed name
        value (bool): The selection status
    """

    name: str
    display_name: str
    value: bool


class CheckboxFrame(ttk.Labelframe):
    """Displays multiple checkboxes below each other.

    The checkboxes are grouped in a labeled Frame with the
    group name as title. Only CheckboxGroupValue in the
    correct group are displayed, others get ignored.
    """

    def __init__(
        self,
        master: Any,
        values: list[CheckboxGroupValue],
        groupName: str,
    ):
        """Creates a checkbox frame.

        Args:
            master (Any): The ttk widget to use as root
            values (list[CheckboxGroupValue]): A list of CheckboxGroupValue to scan for relevant entries
            groupName (str): The group name of the frame
        """
        super().__init__(master, text=groupName)
        self.input_values = list(filter(lambda x: x.group == groupName, values))
        self.values: list[CheckboxRawValue] = []

        for i, value in enumerate(self.input_values):
            var = ttk.BooleanVar(value=value.default)
            checkbox = ttk.Checkbutton(
                self,
                text=value.display_name,
                variable=var,
            )

            checkbox.grid(row=i, column=0, padx=10, pady=2, sticky="w")
            self.values.append(
                CheckboxRawValue(
                    name=value.name, display_name=value.display_name, value=var
                )
            )

    def get(self) -> dict[str, CheckboxValue]:
        """Returns the current state of the selections.

        Returns:
            dict[str, CheckboxValue]: The current state
        """
        values: dict[str, CheckboxValue] = {}
        for value in self.values:
            values.update(
                {
                    value.name: CheckboxValue(
                        name=value.name,
                        display_name=value.display_name,
                        value=value.value.get(),
                    )
                }
            )
        return values


class HorizontalCheckboxFrame(ttk.Labelframe):
    """Displays multiple checkboxes next to each other.

    The checkboxes are grouped in a labeled Frame with the
    group name as title. Only CheckboxGroupValue in the
    correct group are displayed, others get ignored.

    The labels for the checkboxes are rendered above instead
    of to the right.
    """

    def __init__(
        self,
        master: Any,
        values: list[CheckboxGroupValue],
        groupName: str,
        options_per_row: int = 0,
    ):
        """Creates a horizontal checkbox frame.

        Args:
            master (Any): The ttk widget to use as root
            values (list[CheckboxGroupValue]): A list of CheckboxGroupValue to scan for relevant entries
            groupName (str): The group name of the frame
            options_per_row (int): How many checkboxes to display in a row, 0 to only use one row (Default is 0)
        """
        super().__init__(master, text=groupName)
        self.input_values = list(filter(lambda x: x.group == groupName, values))
        self.values: list[CheckboxRawValue] = []

        actual_options_per_row = (
            options_per_row if options_per_row > 0 else len(self.input_values)
        )

        for i in range(0, actual_options_per_row):
            self.columnconfigure(i, weight=1, uniform=f"{groupName}-element-width")

        cur_row = 0

        for i, value in enumerate(self.input_values):
            cur_col = i % actual_options_per_row

            label = ttk.Label(self, text=value.display_name)
            label.grid(row=cur_row, column=cur_col, padx=10, pady=2)

            var = ttk.BooleanVar(value=value.default)
            checkbox = ttk.Checkbutton(
                self,
                text="",
                variable=var,
            )

            checkbox.grid(row=cur_row + 1, column=cur_col, padx=10, pady=2)
            self.values.append(
                CheckboxRawValue(
                    name=value.name, display_name=value.display_name, value=var
                )
            )

            if (i + 1) % actual_options_per_row == 0:
                cur_row += 2

    def get(self) -> dict[str, CheckboxValue]:
        """Returns the current state of the selections.

        Returns:
            dict[str, CheckboxValue]: The current state
        """
        values: dict[str, CheckboxValue] = {}
        for value in self.values:
            values.update(
                {
                    value.name: CheckboxValue(
                        name=value.name,
                        display_name=value.display_name,
                        value=value.value.get(),
                    )
                }
            )
        return values
