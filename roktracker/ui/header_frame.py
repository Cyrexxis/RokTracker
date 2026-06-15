"""Header frame widget for the rok tracker GUI.

Displays the application title as a styled label and a theme
selector combobox. The switch_theme method updates the window
theme when the user selects a different option."""

from typing import Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import PRIMARY

from roktracker.ui.config import AVAILABLE_THEMES


class HeaderFrame(ttk.Frame):
    """Shows a title with a theme selection."""

    def __init__(self, master: Any, default_theme: str):
        """Creates a header frame.

        Args:
            master (Any): The ttk widget to use as root
            default_theme (str): The theme to use as default for the combobox
        """
        super().__init__(master)
        self.master = master

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        title_label = ttk.Label(
            self,
            text="ROK Scanner",
            font=("", 24, "bold"),
            bootstyle=PRIMARY,
        )
        title_label.grid(row=0, column=0, sticky="w")

        self.theme = ttk.StringVar(value=default_theme)

        theme_combo = ttk.Combobox(
            self,
            textvariable=self.theme,
            values=AVAILABLE_THEMES,
            state="readonly",
            width=14,
        )
        theme_combo.grid(row=0, column=1, sticky="e")
        theme_combo.bind("<<ComboboxSelected>>", self._switch_theme)

    def _switch_theme(self, *_: Any) -> None:
        """Switches the theme to the currently selected one.

        Args:
            *_ (Any): Not used
        """
        self.master.style.theme_use(self.theme.get())  # type: ignore
