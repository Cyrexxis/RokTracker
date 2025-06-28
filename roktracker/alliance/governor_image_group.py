from cv2.typing import MatLike
from dataclasses import dataclass


@dataclass
class GovImageGroup:
    score_img: MatLike
