from dataclasses import dataclass
from typing import Any

import ttkbootstrap as ttk


@dataclass
class InfoValue:
    name: str
    display_name: str
    value: str


@dataclass
class RawInfoValue:
    display_name: ttk.StringVar
    value: ttk.StringVar


@dataclass
class AdditionalInfoData:
    current_time: str = "Now"
    eta_remaining: str = "Later"
    current_amount: int = 0
    target_amount: int = 300
    skipped: int = -1


@dataclass
class AdditionalInfoRawData:
    current_time: ttk.StringVar
    eta_remaining: ttk.StringVar
    amount: ttk.StringVar
    skipped: ttk.StringVar


class AdditionalStatusInfo(ttk.Frame):
    def __init__(self, master: Any, id: str, data: AdditionalInfoData):
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
        self.values.current_time.set(new_status.current_time)
        self.values.eta_remaining.set(new_status.eta_remaining)
        self.values.amount.set(
            f"{new_status.current_amount} of {new_status.target_amount}"
        )
        self.values.skipped.set(self._process_skip_text(new_status))

    def _process_skip_text(self, status: AdditionalInfoData) -> str:
        return f"Skipped: {status.skipped}" if status.skipped >= 0 else ""


class StatusInfoFrame(ttk.Frame):
    def __init__(
        self, master: Any, id: str, values: list[InfoValue], extra: AdditionalInfoData
    ):
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
        for info_value in status:
            data = self.status.get(info_value.name)
            if data is not None:
                data.display_name.set(info_value.display_name)
                data.value.set(info_value.value)

        if extra is not None:
            self.additional_stats.update_status(extra)
