from pydantic import BaseModel
from typing import Dict, List, Optional


class TimingsConfig(BaseModel):
    gov_open: float = 2.0
    copy_wait: float = 0.2
    kills_open: float = 1.0
    info_open: float = 1.0
    info_close: float = 0.5
    gov_close: float = 1.0
    max_random: float = 0.5


class FormatsConfig(BaseModel):
    xlsx: bool = True
    csv: bool = False
    jsonl: bool = False

    def from_list(self, list: List[str]):
        for item in list:
            if item == "xlsx":
                self.xlsx = True
            elif item == "csv":
                self.csv = True
            elif item == "jsonl":
                self.jsonl = True

    def from_dict(self, dict: Dict[str, bool]):
        for key, value in dict.items():
            if key == "xlsx":
                self.xlsx = value
            elif key == "csv":
                self.csv = value
            elif key == "jsonl":
                self.jsonl = value


class ScanConfig(BaseModel):
    kingdom_name: str = ""
    people_to_scan: int = 300
    resume: bool = False
    advanced_scroll: bool = True
    track_inactives: bool = False
    validate_power: bool = False
    power_threshold: int = 100000
    validate_kills: bool = True
    reconstruct_kills: bool = True
    timings: TimingsConfig
    formats: FormatsConfig


class BluestacksConfig(BaseModel):
    name: str = "RoK Tracker"
    config: str = "C:\\ProgramData\\BlueStacks_nxt\\bluestacks.conf"


class GeneralConfig(BaseModel):
    emulator: str = "bluestacks"
    bluestacks: BluestacksConfig
    adb_port: int = 5555


class FullConfig(BaseModel):
    scan: ScanConfig
    general: GeneralConfig
