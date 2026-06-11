from dataclasses import dataclass


@dataclass
class RankingData:
    img_path: str
    name: str
    score: str
