from dataclasses import dataclass
from typing import List, Tuple
from dummy_root import get_app_root


@dataclass
class KingdomMisc:
    threshold: int = 90
    invert: bool = True
    script: str = "alliance_6_person_scroll.txt"


class KingdomUI:
    name_normal: List[Tuple[int, int, int, int]] = [
        (334, 260, 293, 33),
        (334, 359, 293, 33),
        (334, 460, 293, 33),
        (334, 562, 293, 33),
        (334, 662, 293, 33),
        (334, 763, 293, 33),
    ]
    score_normal: List[Tuple[int, int, int, int]] = [
        (1087, 269, 250, 33),
        (1087, 368, 250, 33),
        (1087, 469, 250, 33),
        (1087, 571, 250, 33),
        (1087, 671, 250, 33),
        (1087, 772, 250, 33),
    ]
    name_last: List[Tuple[int, int, int, int]] = [
        (334, 283, 293, 33),
        (334, 383, 293, 33),
        (334, 483, 293, 33),
        (334, 585, 293, 33),
        (334, 685, 293, 33),
        (334, 785, 293, 33),
    ]
    score_last: List[Tuple[int, int, int, int]] = [
        (1087, 292, 250, 33),
        (1087, 392, 250, 33),
        (1087, 492, 250, 33),
        (1087, 594, 250, 33),
        (1087, 694, 250, 33),
        (1087, 794, 250, 33),
    ]
    misc = KingdomMisc()
