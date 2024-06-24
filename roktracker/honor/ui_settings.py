from dataclasses import dataclass
from typing import List, Tuple
from dummy_root import get_app_root


@dataclass
class HonorMisc:
    threshold: int = 150
    invert: bool = False
    script: str = "honor_5_person_scroll.txt"


class HonorUI:
    name: List[Tuple[int, int, int, int]] = [
        (774, 324, 257, 40),
        (774, 424, 257, 40),
        (774, 524, 257, 40),
        (774, 624, 257, 40),
        (774, 724, 257, 40),
    ]
    score: List[Tuple[int, int, int, int]] = [
        (1183, 324, 178, 40),
        (1183, 424, 178, 40),
        (1183, 524, 178, 40),
        (1183, 624, 178, 40),
        (1183, 724, 178, 40),
    ]
    misc = HonorMisc()
