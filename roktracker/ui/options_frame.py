"""Options frame widget for displaying editable configuration values.

Provides the OptionsFrame class with a list of editable options
(text, int, float, bool). Supports converting from CheckboxValue
via from_checkbox() and updating individual options."""

from dataclasses import dataclass
from typing import Any

import ttkbootstrap as ttk

from roktracker.ui.checkbox_frames import CheckboxValue
from roktracker.utils.general import is_string_float, is_string_int


@dataclass
class OptionsElement:
    """A option to display.

    Attributes:
        name (str): Internal name
        display_name (str): Displayed name
        value (str | int | float | bool): Current value
        editable (bool): Option can be changed
    """

    name: str
    display_name: str
    value: str | int | float | bool
    editable: bool = True

    @staticmethod
    def from_checkbox(input: CheckboxValue) -> OptionsElement:
        """Creates an OptionsElement from a CheckboxValue.

        Everything from the CheckboxValue is used as is
        and the Option is marked as editable.

        Args:
            input (CheckboxValue): The original CheckboxValue

        Returns:
            OptionsElement: Converted OptionsElement
        """
        return OptionsElement(
            name=input.name, display_name=input.display_name, value=input.value
        )

    @staticmethod
    def from_checkboxes(input: dict[str, CheckboxValue]) -> dict[str, OptionsElement]:
        """Creates a dict of OptionElements from a dict of CheckboxValues.

        The dict keys of the result and the input are the same.

        Args:
            input (dict[str, CheckboxValue]): The input dict

        Returns:
            dict[str, OptionsElement]: The converted OptionsElement dict
        """
        options: dict[str, OptionsElement] = {}
        for value in input.values():
            options.update({value.name: OptionsElement.from_checkbox(value)})
        return options


@dataclass
class OptionsRawElement:
    """The raw version of an OptionsElement.

    Attributes:
        name (str): The internal name
        display_name (str): The displayed name
        value (ttk.StringVar | ttk.IntVar | ttk.DoubleVar | ttk.BooleanVar): The ttk variable with the current value
    """

    name: str
    display_name: str
    value: ttk.StringVar | ttk.IntVar | ttk.DoubleVar | ttk.BooleanVar


class OptionsFrame(ttk.Frame):
    """A frame that shows a list of options."""

    def __init__(self, master: Any, config: list[OptionsElement]):
        """Creates a options frame.

        Args:
            master (Any): The ttk widget to use as root
            config (list[OptionsElement]): The list of options to display
        """
        super().__init__(master)
        self.config = config
        self.values: list[OptionsRawElement] = []

        self.int_validation = self.register(is_string_int)
        self.float_validation = self.register(is_string_float)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        for i, value in enumerate(config):
            element_label = ttk.Label(self, text=value.display_name)
            element_label.grid(row=i, column=0, padx=10, pady=(5, 0), sticky="w")

            if isinstance(value.value, bool):
                element_variable = ttk.BooleanVar(self, value.value)
                element_field = ttk.Checkbutton(
                    self, text="", variable=element_variable
                )
                element_field.grid(row=i, column=1, padx=10, pady=(5, 0), sticky="w")

            elif isinstance(value.value, int):
                element_variable = ttk.IntVar(self, value.value)

                element_field = ttk.Entry(
                    self,
                    textvariable=element_variable,
                    validate="all",
                    validatecommand=(self.int_validation, "%P", True),
                )
                element_field.grid(row=i, column=1, padx=10, pady=(5, 0), sticky="ew")

            elif isinstance(value.value, float):
                element_variable = ttk.DoubleVar(self, value.value)

                element_field = ttk.Entry(
                    self,
                    textvariable=element_variable,
                    validate="all",
                    validatecommand=(self.float_validation, "%P", True),
                )
                element_field.grid(row=i, column=1, padx=10, pady=(5, 0), sticky="ew")

            else:
                element_variable = ttk.StringVar(self, value.value)

                if value.editable:
                    element_field = ttk.Entry(self, textvariable=element_variable)
                    element_field.grid(
                        row=i, column=1, padx=10, pady=(5, 0), sticky="ew"
                    )

                else:
                    element_label_2 = ttk.Label(
                        self, textvariable=element_variable, anchor="w"
                    )
                    element_label_2.grid(
                        row=i, column=1, padx=10, pady=(5, 0), sticky="ew"
                    )

            self.values.append(
                OptionsRawElement(
                    name=value.name,
                    display_name=value.display_name,
                    value=element_variable,
                )
            )

    def set_option(self, option: OptionsElement):
        """Sets the corresponding option to a new value.

        The option gets only updated if it is present in the
        current options and the type matches the current type.

        Args:
            option (OptionsElement): The new option
        """
        for opt in self.values:
            if opt.name == option.name and type(opt.value.get()) is type(option.value):
                opt.value.set(option.value)  # type: ignore (The type check should fetch a type mismatch)

    def get_options(self) -> dict[str, OptionsElement]:
        """Processes the current state and returns it.

        Returns:
            dict[str, OptionsElement]: Current state of the options.
                The internal name is used as key for the dict.
        """
        options: dict[str, OptionsElement] = {}

        for option in self.values:
            options.update(
                {
                    option.name: OptionsElement(
                        name=option.name,
                        display_name=option.display_name,
                        value=option.value.get(),
                    )
                }
            )

        return options
