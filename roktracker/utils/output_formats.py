from dataclasses import dataclass
from typing import Dict, List


@dataclass
class OutputFormats:
    xlsx: bool = False
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
