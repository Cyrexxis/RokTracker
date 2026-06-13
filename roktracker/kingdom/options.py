from pathlib import Path

from pydantic import BaseModel

from roktracker.common.output_formats import OutputFormats

STAT_LABELS: dict[str, str] = {
    "ID": "id",
    "Name": "name",
    "Power": "power",
    "Killpoints": "killpoints",
    "Acclaim": "acclaim",
    "Highest Acclaim": "acclaim_max",
    "Alliance": "alliance",
    "T1 Kills": "t1_kills",
    "T2 Kills": "t2_kills",
    "T3 Kills": "t3_kills",
    "T4 Kills": "t4_kills",
    "T5 Kills": "t5_kills",
    "Ranged": "ranged_points",
    "Deads": "deads",
    "Rss Assistance": "assisted",
    "Rss Gathered": "gathered",
    "Helps": "helps",
}


class StatsToScan(BaseModel):
    # first screen
    id: bool = True
    name: bool = True
    power: bool = True
    killpoints: bool = True
    acclaim: bool = True
    acclaim_max: bool = True
    alliance: bool = True

    # second screen
    t1_kills: bool = True
    t2_kills: bool = True
    t3_kills: bool = True
    t4_kills: bool = True
    t5_kills: bool = True
    ranged_points: bool = True

    # third screen
    deads: bool = True
    gathered: bool = True
    assisted: bool = True
    helps: bool = True

    @staticmethod
    def nothing() -> StatsToScan:
        return StatsToScan(
            id=False,
            name=False,
            power=False,
            killpoints=False,
            acclaim=False,
            acclaim_max=False,
            alliance=False,
            t1_kills=False,
            t2_kills=False,
            t3_kills=False,
            t4_kills=False,
            t5_kills=False,
            ranged_points=False,
            deads=False,
            assisted=False,
            gathered=False,
            helps=False,
        )


class KingdomScanOptions(BaseModel):
    scan_name: str = ""
    amount: int = 300
    stats_to_scan: StatsToScan = StatsToScan()
    continued: bool = False
    track_inactives: bool = False
    validate_kills: bool = True
    reconstruct_kills: bool = True
    validate_power: bool = False
    power_threshold: int = 100_000
    advanced_scroll: bool = True
    formats: OutputFormats = OutputFormats()

    @staticmethod
    def from_json(path: str | Path) -> KingdomScanOptions:
        data = Path(path).read_text(encoding="utf-8")
        return KingdomScanOptions.model_validate_json(data)
