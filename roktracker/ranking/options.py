"""User-facing options for ranking scan configuration.

Defines the RankingScanOptions class with settings for scan
name, target count, and output formats. Supports loading
from JSON files."""

from pathlib import Path

from pydantic import BaseModel

from roktracker.common.output_formats import OutputFormats


class RankingScanOptions(BaseModel):
    """Configuration options for a ranking scan.

    Attributes:
        scan_name (str): The name of the scan, used in the file name
        amount (int): How many governors should be scanned
        formats (OutputFormats): What formats to use for saving
    """

    scan_name: str = ""
    amount: int = 100
    formats: OutputFormats = OutputFormats()

    @staticmethod
    def from_json(path: str | Path) -> RankingScanOptions:
        """Load and validate a RankingScanOptions from a JSON file.

        Args:
            path (str | Path): A string or Path object to the json file

        Returns:
            RankingScanOptions: The loaded and validated RankingScanOptions
        """
        data = Path(path).read_text(encoding="utf-8")
        return RankingScanOptions.model_validate_json(data)
