from cv2.typing import MatLike
from dataclasses import dataclass


@dataclass
class GovImageGroup:
    name_img: MatLike
    name_img_small: MatLike
    score_img: MatLike
