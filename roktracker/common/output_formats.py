from pydantic import BaseModel


class OutputFormats(BaseModel):
    xlsx: bool = True
    csv: bool = False
    jsonl: bool = False

    def from_list(self, list: list[str]):
        for item in list:
            if item == "xlsx":
                self.xlsx = True
            elif item == "csv":
                self.csv = True
            elif item == "jsonl":
                self.jsonl = True

    def from_dict(self, dict: dict[str, bool]):
        for key, value in dict.items():
            if key == "xlsx":
                self.xlsx = value
            elif key == "csv":
                self.csv = value
            elif key == "jsonl":
                self.jsonl = value
