import datetime
import math
import re
import time
from pathlib import Path
from typing import Callable, List, Literal

import cv2
from cv2.typing import MatLike
from PIL import Image
from tesserocr import OEM, PSM, PyTessBaseAPI

import roktracker.utils.ocr as ocr
from dummy_root import get_app_root
from roktracker.common.config import AppConfig
from roktracker.ranking.config import RankingConfig
from roktracker.ranking.options import RankingScanOptions
from roktracker.ranking.ranking_data import AdditionalRankingData, RankingData
from roktracker.ranking.ranking_data_handler import RankingDataHandler
from roktracker.utils.adb import AdvancedAdbClient
from roktracker.utils.general import (
    generate_random_id,
    load_cv2_img,
    wait_random_range,
    write_cv2_img,
)


class RankingScanner:
    """Base class for all list-based ranking scanners (alliance, seed, honor).

    KingdomScanner is deliberately excluded — it's an interactive profile scanner
    with fundamentally different flow (open profile → navigate tabs → close profile).
    """

    def __init__(self, config: AppConfig, cfg: RankingConfig):
        self.run_id = generate_random_id(8)
        self.start_date = datetime.date.today()
        self.stop_scan = False
        self.scan_times: list[float] = []
        self.reached_bottom: bool = False
        self.govs_per_screen = cfg.govs_per_screen
        self.screens_needed = 0
        self.max_random_delay = config.timings.max_random
        self.cfg = cfg

        self.root_dir = get_app_root()
        self.tesseract_path = Path(self.root_dir / "deps" / "tessdata")
        self.img_path = Path(self.root_dir / "temp_images")
        self.img_path.mkdir(parents=True, exist_ok=True)
        self.scan_path = Path(self.root_dir / cfg.scan_path)
        self.scan_path.mkdir(parents=True, exist_ok=True)

        self.batch_callback: Callable[
            [List[RankingData], AdditionalRankingData], None
        ] = lambda g, e: None
        self.state_callback: Callable[[str], None] = lambda m: None
        self.output_handler: Callable[[str], None] = lambda m: None

        adb_path = str(self.root_dir / "deps" / "platform-tools" / "adb.exe")

        self.adb_client = AdvancedAdbClient(
            adb_path,
            config.general.adb_port,
            config.general.emulator,
            self.root_dir / "deps" / "inputs",
        )

    # -- Callback setters (identical, no override needed) --
    def set_batch_callback(
        self, cb: Callable[[List[RankingData], AdditionalRankingData], None]
    ) -> None:
        self.batch_callback = cb

    def set_state_callback(self, cb: Callable[[str], None]) -> None:
        self.state_callback = cb

    def set_output_handler(self, cb: Callable[[str], None]) -> None:
        self.output_handler = cb

    # -- Common helpers (identical, no override needed) --
    def get_remaining_time(self, remaining_govs: int) -> float:
        avg = (
            sum(self.scan_times, start=0) / len(self.scan_times)
            if self.scan_times
            else 0
        )
        return avg * remaining_govs

    def _get_roi_region(
        self, gov_index: int, last: bool, kind: Literal["name", "score"]
    ) -> tuple[int, int, int, int]:
        """Return a (x, y, w, h) tuple for the given governor position.

        kind is "name", "name_small", or "score".
        """
        if kind == "name":
            return (
                self.cfg.ui_config.name_last
                if (last and self.cfg.last_different)
                else self.cfg.ui_config.name_normal
            )[gov_index]
        if kind == "score":
            return (
                self.cfg.ui_config.score_last
                if (last and self.cfg.last_different)
                else self.cfg.ui_config.score_normal
            )[gov_index]
        raise ValueError(f"Unknown kind: {kind}")

    def _check_for_last_screen(self, image: MatLike) -> None:
        roi_score = self._get_roi_region(0, False, "score")
        score_raw = ocr.cropToRegion(image, roi_score)
        score_bw = ocr.preprocessImage(
            score_raw, 3, self.cfg.misc.threshold, 12, self.cfg.misc.invert
        )
        with PyTessBaseAPI(
            path=str(self.tesseract_path), psm=PSM.SINGLE_WORD, oem=OEM.LSTM_ONLY
        ) as api:
            api.SetImage(Image.fromarray(score_bw))  # type: ignore (Incorrectly typed in pytesseract)
            test_score = re.sub("[^0-9]", "", api.GetUTF8Text())
            if test_score == "":
                self.reached_bottom = True

    # -- Core: screenshot + OCR for one screen (nearly identical) --
    def _scan_screen(self, screen_number: int) -> List[RankingData]:
        self.adb_client.secure_adb_screencap().save(self.img_path / "currentState.png")
        image = load_cv2_img(self.img_path / "currentState.png", cv2.IMREAD_UNCHANGED)

        # Detect last screen by checking if first score is empty
        self._check_for_last_screen(image)

        govs: List[RankingData] = []
        with PyTessBaseAPI(
            path=str(self.tesseract_path), psm=PSM.SINGLE_LINE, oem=OEM.LSTM_ONLY
        ) as api:
            for gov_number in range(self.govs_per_screen):
                roi_name = self._get_roi_region(gov_number, self.reached_bottom, "name")
                roi_score = self._get_roi_region(
                    gov_number, self.reached_bottom, "score"
                )

                name_raw = ocr.cropToRegion(image, roi_name)
                score_raw = ocr.cropToRegion(image, roi_score)

                name_bw = ocr.preprocessImage(
                    name_raw, 3, self.cfg.misc.threshold, 12, self.cfg.misc.invert
                )
                name_small_bw = ocr.preprocessImage(
                    name_raw, 1, self.cfg.misc.threshold, 4, self.cfg.misc.invert
                )
                score_bw = ocr.preprocessImage(
                    score_raw, 3, self.cfg.misc.threshold, 12, self.cfg.misc.invert
                )

                api.SetPageSegMode(PSM.SINGLE_LINE)
                gov_name = ocr.ocr_text(api, name_bw)

                api.SetPageSegMode(PSM.SINGLE_WORD)
                gov_score = ocr.ocr_number(api, score_bw)

                gov_img_path = str(
                    self.img_path
                    / f"gov_name_{(self.govs_per_screen * screen_number) + gov_number}.png"
                )
                write_cv2_img(name_small_bw, gov_img_path, "png")

                govs.append(RankingData(gov_img_path, gov_name, gov_score))

        return govs

    def _scroll_action(self) -> None:
        """Perform the scroll after processing a screen."""
        self.adb_client.adb_send_events("Touch", self.cfg.misc.script)

    def _make_filename(self, amount: int, kingdom: str) -> str:
        return f"{self.cfg.filename_prefix}{amount}-{self.start_date}-{kingdom}-[{self.run_id}]"

    def _make_additional_data(
        self, page: int, total_pages: int
    ) -> AdditionalRankingData:
        return AdditionalRankingData(
            page,
            total_pages,
            self.govs_per_screen,
            self.get_remaining_time(total_pages - page),
        )

    # -- Main scan loop (identical, no override needed) --
    def start_scan(self, options: RankingScanOptions):
        self.state_callback("Initializing")
        self.adb_client.start_adb()
        self.screens_needed = int(math.ceil(options.amount / self.govs_per_screen))

        filename = self._make_filename(options.amount, options.scan_name)
        data_handler = RankingDataHandler(self.scan_path, filename, options.formats)

        self.state_callback("Scanning")

        for i in range(self.screens_needed):
            if self.stop_scan:
                self.output_handler("Scan Terminated! Saving current progress...")
                break

            start_time = time.time()
            governors = self._scan_screen(i)
            end_time = time.time()
            self.scan_times.append(end_time - start_time)

            additional_data = self._make_additional_data(i, self.screens_needed)
            self.batch_callback(governors, additional_data)

            self.reached_bottom = (
                data_handler.write_governors(governors) or self.reached_bottom
            )
            data_handler.save()

            if not self.reached_bottom:
                self._scroll_action()
                wait_random_range(1, self.max_random_delay)

        data_handler.save()
        self.adb_client.kill_adb()
        for p in self.img_path.glob("gov_name*.png"):
            p.unlink()
        self.state_callback("Scan finished")

    def end_scan(self) -> None:
        self.stop_scan = True
