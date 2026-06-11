from dataclasses import dataclass
from typing import Any

import ttkbootstrap as ttk


@dataclass
class CheckboxGroupValue:
    name: str
    display_name: str
    group: str
    default: bool


@dataclass
class CheckboxRawValue:
    name: str
    display_name: str
    value: ttk.BooleanVar


@dataclass
class CheckboxValue:
    name: str
    display_name: str
    value: bool


class CheckboxFrame(ttk.Labelframe):
    def __init__(
        self,
        master: Any,
        values: list[CheckboxGroupValue],
        groupName: str,
    ):
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
    def __init__(
        self,
        master: Any,
        values: list[CheckboxGroupValue],
        groupName: str,
        options_per_row: int = 0,
    ):
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
