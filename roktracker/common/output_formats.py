"""Pydantic models for configuring scan export formats.

Exports the OutputFormats class and convenience constructors
from_list() and from_dict() for selecting Excel, CSV, and
other output formats."""

from pydantic import BaseModel


class OutputFormats(BaseModel):
    """Configurable set of output formats for scan results."""

    xlsx: bool = True
    csv: bool = False
    jsonl: bool = False

    @staticmethod
    def from_list(formats: list[str]) -> OutputFormats:
        """Initializes a model by iteration over a list of supported formats.

        Args:
            formats (list[str]): List of format strings (e.g. ``["xlsx", "csv"]``).

        Returns:
            OutputFormats: The new model
        """
        output_formats = OutputFormats(xlsx=False, csv=False, jsonl=False)
        for item in formats:
            if item == "xlsx":
                output_formats.xlsx = True
            elif item == "csv":
                output_formats.csv = True
            elif item == "jsonl":
                output_formats.jsonl = True

        return output_formats

    @staticmethod
    def from_dict(mapping: dict[str, bool]) -> OutputFormats:
        """Initializes a model by iterating over a key-value mapping.

        Args:
            mapping (dict[str, bool]): A dictionary mapping format names to booleans.

        Returns:
            OutputFormats: The new model
        """
        output_formats = OutputFormats(xlsx=False, csv=False, jsonl=False)
        for key, value in mapping.items():
            if key == "xlsx":
                output_formats.xlsx = value
            elif key == "csv":
                output_formats.csv = value
            elif key == "jsonl":
                output_formats.jsonl = value

        return output_formats
