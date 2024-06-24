from dataclasses import dataclass
from typing import List, Tuple
from dummy_root import get_app_root


@dataclass
class AllianceMisc:
    threshold: int = 90
    invert: bool = True
    script: str = "alliance_6_person_scroll.txt"


class AllianceUI:
    name_normal: List[Tuple[int, int, int, int]] = [
        (334, 260, 293, 33),
        (334, 359, 293, 33),
        (334, 460, 293, 33),
        (334, 562, 293, 33),
        (334, 662, 293, 33),
        (334, 763, 293, 33),
    ]
    score_normal: List[Tuple[int, int, int, int]] = [
        (1117, 265, 250, 33),
        (1117, 364, 250, 33),
        (1117, 465, 250, 33),
        (1117, 567, 250, 33),
        (1117, 667, 250, 33),
        (1117, 768, 250, 33),
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
        (1117, 288, 250, 33),
        (1117, 388, 250, 33),
        (1117, 488, 250, 33),
        (1117, 590, 250, 33),
        (1117, 690, 250, 33),
        (1117, 790, 250, 33),
    ]
    misc = AllianceMisc()
