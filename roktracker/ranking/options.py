from pathlib import Path

from pydantic import BaseModel

from roktracker.common.output_formats import OutputFormats


class RankingScanOptions(BaseModel):
    scan_name: str = ""
    amount: int = 100
    formats: OutputFormats = OutputFormats()

    @staticmethod
    def from_json(path: str | Path) -> RankingScanOptions:
        data = Path(path).read_text(encoding="utf-8")
        return RankingScanOptions.model_validate_json(data)
