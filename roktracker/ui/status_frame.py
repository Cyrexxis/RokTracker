"""Status display components for the scanner GUI.

Provides InfoValue and AdditionalInfoData for displaying scan
progress, ETA, and skip counts. The StatusInfoFrame and
AdditionalStatusInfo classes render this data in the UI with
update_status() for live refreshes."""

from dataclasses import dataclass
from typing import Any

import ttkbootstrap as ttk


@dataclass
class InfoValue:
    """General info value.

    Attributes:
        name (str): The internal name
        display_name (str): The displayed name
        value (str): The displayed value
    """

    name: str
    display_name: str
    value: str


@dataclass
class RawInfoValue:
    """Raw version of an InfoValue.

    Attributes:
        display_name (ttk.StringVar): The ttk variable that holds the displayed name
        value (ttk.StringVar): The ttk variable that holds the displayed value
    """

    display_name: ttk.StringVar
    value: ttk.StringVar


@dataclass
class AdditionalInfoData:
    """Additional info data.

    Attributes:
        current_time (str): The time of the update
        eta_remaining (str): The estimated time needed to finish the scan
        current_amount (int): The current position in the scan
        target_amount (int): The final position to scan
        skipped (int): How many governors were skipped
    """

    current_time: str = "Now"
    eta_remaining: str = "Later"
    current_amount: int = 0
    target_amount: int = 300
    skipped: int = -1


@dataclass
class AdditionalInfoRawData:
    """Raw version of the additional info data.

    Attributes:
        current_time (ttk.StringVar): The ttk variable that holds the current time
        eta_remaining (ttk.StringVar): The ttk variable that holds the eta
        amount (ttk.StringVar): The ttk variable that holds computed value of current and total count
        skipped (ttk.StringVar): The ttk variable that holds the skipped amount
    """

    current_time: ttk.StringVar
    eta_remaining: ttk.StringVar
    amount: ttk.StringVar
    skipped: ttk.StringVar


class AdditionalStatusInfo(ttk.Frame):
    """Displays additional data for the current state of the scanner."""

    def __init__(self, master: Any, id: str, data: AdditionalInfoData):
        """Creates a additional status info frame.

        Args:
            master (Any): The ttk widget to use as root
            id (str): The id to use (should be unique in the app)
            data (AdditionalInfoData): The additional status to display initially
        """
        super().__init__(master)
        self.values: AdditionalInfoRawData
        self.grid_columnconfigure(0, weight=1, uniform=f"{id}-element-width")
        self.grid_columnconfigure(1, weight=1, uniform=f"{id}-element-width")
        self.grid_columnconfigure(2, weight=1, uniform=f"{id}-element-width")

        amount_processed = f"{data.current_amount} of {data.target_amount}"

        self.values = AdditionalInfoRawData(
            current_time=ttk.StringVar(self, value=data.current_time),
            eta_remaining=ttk.StringVar(self, value=data.eta_remaining),
            amount=ttk.StringVar(self, value=amount_processed),
            skipped=ttk.StringVar(self, value=self._process_skip_text(data)),
        )

        current_time_label = ttk.Label(self, text="Current time")
        current_time_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        current_time_text = ttk.Label(self, textvariable=self.values.current_time)
        current_time_text.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        eta_label = ttk.Label(self, text="ETA")
        eta_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")

        eta_text = ttk.Label(self, textvariable=self.values.eta_remaining)
        eta_text.grid(row=1, column=2, padx=10, pady=5, sticky="e")

        amount_text = ttk.Label(self, textvariable=self.values.amount)
        amount_text.grid(row=0, column=1, pady=5)

        skipped_text = ttk.Label(self, textvariable=self.values.skipped)
        skipped_text.grid(row=1, column=1, pady=5)

    def update_status(self, new_status: AdditionalInfoData):
        """Updates the displayed state.

        Args:
            new_status (AdditionalInfoData): The new state
        """
        self.values.current_time.set(new_status.current_time)
        self.values.eta_remaining.set(new_status.eta_remaining)
        self.values.amount.set(
            f"{new_status.current_amount} of {new_status.target_amount}"
        )
        self.values.skipped.set(self._process_skip_text(new_status))

    def _process_skip_text(self, status: AdditionalInfoData) -> str:
        """Computes the value for the "skipped" text.

        Args:
            status (AdditionalInfoData): The additional data to use

        Returns:
            str: The computed value
        """
        return f"Skipped: {status.skipped}" if status.skipped >= 0 else ""


class StatusInfoFrame(ttk.Frame):
    """Displays current state of the scanner."""

    def __init__(
        self, master: Any, id: str, values: list[InfoValue], extra: AdditionalInfoData
    ):
        """Creates a status info frame.

        It is important to have dummy values for all displayed values,
        because the frame only sets up the display for the values that
        are present during initialization.

        If values that do not match those are provided during an update
        they simply get discarded.

        Args:
            master (Any): The ttk widget to use as root
            id (str): The id to use (should be unique in the app)
            values (list[InfoValue]): The info values to display
            extra (AdditionalInfoData): The additional info to display
        """
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.status: dict[str, RawInfoValue] = {}

        self.additional_stats = AdditionalStatusInfo(self, id, extra)
        self.additional_stats.grid(
            row=0, column=0, columnspan=2, pady=(0, 5), sticky="ewsn"
        )

        offset = 1

        for i, value in enumerate(values):
            label_var = ttk.StringVar(master=self, value=value.display_name)
            value_var = ttk.StringVar(master=self, value=value.value)

            label = ttk.Label(self, textvariable=label_var)
            entry = ttk.Label(self, textvariable=value_var)

            label.grid(
                row=i + offset,  # % ceil(len(values) / 2),
                column=0,
                padx=10,
                pady=2,
                sticky="w",
            )
            entry.grid(
                row=i + offset,  # % ceil(len(values) / 2),
                column=1,
                padx=(10, 30),
                pady=2,
                sticky="w",
            )

            self.status.update(
                {value.name: RawInfoValue(display_name=label_var, value=value_var)}
            )

        # Additional Info

    def update_status(
        self, status: list[InfoValue], extra: AdditionalInfoData | None = None
    ):
        """Updates the current state.

        Args:
            status (list[InfoValue]): List of updated values
            extra (AdditionalInfoData | None): New additional info value (Default value = None)
        """
        for info_value in status:
            data = self.status.get(info_value.name)
            if data is not None:
                data.display_name.set(info_value.display_name)
                data.value.set(info_value.value)

        if extra is not None:
            self.additional_stats.update_status(extra)
