from dataclasses import dataclass
from pydantic import BaseModel
from typing import List, Optional
from enum import StrEnum


class ScanItems(StrEnum):
    ID = "ID"
    NAME = "Name"
    POWER = "Power"
    KILLPOINTS = "Killpoints"
    ALLIANCE = "Alliance"
    T1_KILLS = "T1 Kills"
    T2_KILLS = "T2 Kills"
    T3_KILLS = "T3 Kills"
    T4_KILLS = "T4 Kills"
    T5_KILLS = "T5 Kills"
    RANGED = "Ranged"
    DEATHS = "Deaths"
    ASSISTANCE = "Assistance"
    GATHERED = "Gathered"
    HELPS = "Helps"


class ScanPreset(BaseModel):
    name: str
    selections: List[ScanItems]


@dataclass
class ScanOptions:
    id: bool = True
    name: bool = True
    power: bool = True
    killpoints: bool = True
    alliance: bool = True
    t1_kills: bool = True
    t2_kills: bool = True
    t3_kills: bool = True
    t4_kills: bool = True
    t5_kills: bool = True
    ranged: bool = True
    deaths: bool = True
    assistance: bool = True
    gathered: bool = True
    helps: bool = True
