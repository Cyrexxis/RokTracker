import threading
from typing import Any

import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox

from roktracker.common.config import AppConfig
from roktracker.common.data import AdditionalScanData
from roktracker.common.output_formats import OutputFormats
from roktracker.kingdom.governor_data import AdditionalGovernorData, GovernorData
from roktracker.kingdom.options import KingdomScanOptions, StatsToScan
from roktracker.ranking.options import RankingScanOptions
from roktracker.ranking.ranking_data import RankingData
from roktracker.ui.checkbox_frames import CheckboxGroupValue
from roktracker.ui.options_frame import OptionsElement
from roktracker.ui.status_frame import AdditionalInfoData, InfoValue


def update_config_option(
    config: Any, update: OptionsElement | None, ignore_additional: bool = True
):
    if update is None:
        return

    if not hasattr(config, update.name):
        if ignore_additional:
            return
        else:
            raise AttributeError("Invalid attribute for config")
    if type(getattr(config, update.name)).__name__ != type(update.value).__name__:
        raise AttributeError("Type mismatch with config")
    setattr(config, update.name, update.value)


def update_config_options(
    config: Any, update: dict[str, OptionsElement], ignore_additional: bool = True
):
    for updated_entry in update.values():
        update_config_option(config, updated_entry, ignore_additional)


def additional_data_to_info(data: AdditionalGovernorData) -> AdditionalInfoData:
    return AdditionalInfoData(
        current_time=data.current_time_str(),
        eta_remaining=data.eta(),
        current_amount=data.current_governor,
        target_amount=data.target_governor,
        skipped=data.skipped_governors,
    )


def governor_to_info(governor: GovernorData) -> list[InfoValue]:
    info_values: list[InfoValue] = []
    info_values.append(InfoValue("id", "ID", governor.id))
    info_values.append(InfoValue("name", "Name", governor.name))
    info_values.append(InfoValue("power", "Power", governor.power))
    info_values.append(InfoValue("killpoints", "Kill Points", governor.killpoints))
    info_values.append(InfoValue("alliance", "Alliance", governor.alliance))
    info_values.append(InfoValue("t1_kills", "T1 Kills", governor.t1_kills))
    info_values.append(InfoValue("t1_kp", "T1 KP", governor.t1_kp))
    info_values.append(InfoValue("t2_kills", "T2 Kills", governor.t2_kills))
    info_values.append(InfoValue("t2_kp", "T2 KP", governor.t2_kp))
    info_values.append(InfoValue("t3_kills", "T3 Kills", governor.t3_kills))
    info_values.append(InfoValue("t3_kp", "T3 KP", governor.t3_kp))
    info_values.append(InfoValue("t4_kills", "T4 Kills", governor.t4_kills))
    info_values.append(InfoValue("t4_kp", "T4 KP", governor.t4_kp))
    info_values.append(InfoValue("t5_kills", "T5 Kills", governor.t5_kills))
    info_values.append(InfoValue("t5_kp", "T5 KP", governor.t5_kp))
    info_values.append(
        InfoValue("ranged_points", "Ranged Points", governor.ranged_points)
    )
    info_values.append(InfoValue("dead", "Dead", governor.dead))
    info_values.append(
        InfoValue("rss_assistance", "RSS Assistance", governor.rss_assistance)
    )
    info_values.append(InfoValue("rss_gathered", "RSS Gathered", governor.rss_gathered))
    info_values.append(InfoValue("helps", "Helps", governor.helps))
    info_values.append(InfoValue("t45_kills", "T4+5 Kills", governor.t45_kills()))
    info_values.append(InfoValue("total_kills", "Total Kills", governor.total_kills()))
    return info_values


def additional_batch_data_to_info(data: AdditionalScanData) -> AdditionalInfoData:
    return AdditionalInfoData(
        current_time=data.current_time_str(),
        eta_remaining=data.eta(),
        current_amount=data.current_governor,
        target_amount=data.target_governor,
    )


def batch_to_info(batch: list[RankingData]) -> list[InfoValue]:
    info_values: list[InfoValue] = []
    for index, governor in enumerate(batch):
        info_values.append(
            InfoValue(f"governor_{index}", governor.name, governor.score)
        )

    if len(batch) < 6:
        for missing in range(len(batch), 6 + 1):
            info_values.append(InfoValue(f"governor-{missing}", "", ""))

    return info_values


def sts_to_checkbox(stats: StatsToScan) -> list[CheckboxGroupValue]:
    info_values: list[CheckboxGroupValue] = []
    info_values.append(CheckboxGroupValue("id", "ID", "First Screen", stats.id))
    info_values.append(CheckboxGroupValue("name", "Name", "First Screen", stats.name))
    info_values.append(
        CheckboxGroupValue("power", "Power", "First Screen", stats.power)
    )
    info_values.append(
        CheckboxGroupValue("killpoints", "Killpoints", "First Screen", stats.killpoints)
    )
    info_values.append(
        CheckboxGroupValue("alliance", "Alliance", "First Screen", stats.alliance)
    )
    info_values.append(
        CheckboxGroupValue("t1_kills", "T1 Kills", "Second Screen", stats.t1_kills)
    )
    info_values.append(
        CheckboxGroupValue("t2_kills", "T2 Kills", "Second Screen", stats.t2_kills)
    )
    info_values.append(
        CheckboxGroupValue("t3_kills", "T3 Kills", "Second Screen", stats.t3_kills)
    )
    info_values.append(
        CheckboxGroupValue("t4_kills", "T4 Kills", "Second Screen", stats.t4_kills)
    )
    info_values.append(
        CheckboxGroupValue("t5_kills", "T5 Kills", "Second Screen", stats.t5_kills)
    )
    info_values.append(
        CheckboxGroupValue(
            "ranged_points", "Ranged Points", "Second Screen", stats.ranged_points
        )
    )
    info_values.append(
        CheckboxGroupValue("deads", "Deads", "Third Screen", stats.deads)
    )
    info_values.append(
        CheckboxGroupValue("gathered", "Rss Gathered", "Third Screen", stats.gathered)
    )
    info_values.append(
        CheckboxGroupValue("assisted", "Rss Assistance", "Third Screen", stats.assisted)
    )
    info_values.append(
        CheckboxGroupValue("helps", "Helps", "Third Screen", stats.helps)
    )
    return info_values


def formats_to_checkbox(formats: OutputFormats) -> list[CheckboxGroupValue]:
    info_values: list[CheckboxGroupValue] = []
    info_values.append(
        CheckboxGroupValue("xlsx", "XLSX", "Output Format", formats.xlsx)
    )
    info_values.append(CheckboxGroupValue("csv", "CSV", "Output Format", formats.csv))
    info_values.append(
        CheckboxGroupValue("jsonl", "JSONL", "Output Format", formats.jsonl)
    )
    return info_values


def ko_to_options(
    app_config: AppConfig, options: KingdomScanOptions
) -> list[OptionsElement]:
    info_values: list[OptionsElement] = []
    info_values.append(OptionsElement("scan_uuid", "Scan UUID", "---", False))
    info_values.append(OptionsElement("scan_name", "Scan Name", options.scan_name))
    info_values.append(
        OptionsElement("name", "Bluestacks name", app_config.general.bluestacks.name)
    )
    info_values.append(
        OptionsElement("adb_port", "ADB Port", app_config.general.adb_port)
    )
    info_values.append(OptionsElement("amount", "Amount", options.amount))
    info_values.append(OptionsElement("continued", "Continued", options.continued))
    info_values.append(
        OptionsElement("track_inactives", "Track Inactives", options.track_inactives)
    )
    info_values.append(
        OptionsElement("validate_kills", "Validate Kills", options.validate_kills)
    )
    info_values.append(
        OptionsElement(
            "reconstruct_kills", "Reconstruct Kills", options.reconstruct_kills
        )
    )
    info_values.append(
        OptionsElement("validate_power", "Validate Power", options.validate_power)
    )
    info_values.append(
        OptionsElement("power_threshold", "Power Threshold", options.power_threshold)
    )
    info_values.append(
        OptionsElement("advanced_scroll", "Advanced Scroll", options.advanced_scroll)
    )
    info_values.append(
        OptionsElement("info_close", "More info wait", app_config.timings.info_close)
    )
    info_values.append(
        OptionsElement("gov_close", "Governor wait", app_config.timings.gov_close)
    )
    return info_values


def ro_to_options(
    app_config: AppConfig, options: RankingScanOptions
) -> list[OptionsElement]:
    info_values: list[OptionsElement] = []
    info_values.append(OptionsElement("scan_uuid", "Scan UUID", "---", False))
    info_values.append(OptionsElement("scan_name", "Scan Name", options.scan_name))
    info_values.append(
        OptionsElement("name", "Bluestacks name", app_config.general.bluestacks.name)
    )
    info_values.append(
        OptionsElement("adb_port", "ADB Port", app_config.general.adb_port)
    )
    info_values.append(OptionsElement("amount", "Amount", options.amount))
    info_values.append(
        OptionsElement("info_close", "More info wait", app_config.timings.info_close)
    )
    info_values.append(
        OptionsElement("gov_close", "Governor wait", app_config.timings.gov_close)
    )
    return info_values


def show_error(parent: ttk.Frame | ttk.Window, message: str, title: str):
    parent.after(
        0,
        lambda: Messagebox.show_error(
            message=message,
            title=title,
            parent=parent,
        ),
    )


def show_confirm(parent: ttk.Frame | ttk.Window, message: str, title: str) -> bool:
    _result = {"value": False}
    _event = threading.Event()

    def show_dialog():
        response = Messagebox.yesno(message, title, True, parent=parent)
        _result["value"] = response == "Yes"
        _event.set()
        parent.focus()

    parent.after(0, show_dialog)
    _event.wait()
    return _result["value"]
