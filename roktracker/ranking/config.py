from pathlib import Path

from pydantic import BaseModel


class RankingMisc(BaseModel):
    threshold: int
    invert: bool
    script: str


class UIConfig(BaseModel):
    name_normal: list[tuple[int, int, int, int]]
    score_normal: list[tuple[int, int, int, int]]

    name_last: list[tuple[int, int, int, int]]
    score_last: list[tuple[int, int, int, int]]


class RankingConfig(BaseModel):
    """Per-scanner configuration. Each subclass provides this."""

    scan_path: str  # e.g. "scans_alliance"
    filename_prefix: str  # e.g. "Alliance"
    govs_per_screen: int  # e.g. 6
    last_different: bool  # True for Alliance/Seed (normal+last ROIs), False for Honor
    ui_config: UIConfig  # Any UI class with .name, .score, .name_last, etc.
    misc: RankingMisc

    @staticmethod
    def from_json(path: str | Path) -> RankingConfig:
        data = Path(path).read_text(encoding="utf-8")
        return RankingConfig.model_validate_json(data)
