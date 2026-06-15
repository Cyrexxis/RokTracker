"""Data models for ranking scan results.

Provides the RankingData class representing a single OCR-
extracted ranking entry with name, score, and a temporary
screenshot image reference."""

from dataclasses import dataclass


@dataclass
class RankingData:
    """Represents the OCR-extracted data for a single ranking entry.

    The type of all attributes is str because the class is intended
    to be used to show the the current state to the user.

    Attributes:
        img_path (str): The path to a temporary image of the name
        name (str): The name of the governor
        score (str): The score of the governor
    """

    img_path: str
    name: str
    score: str
