import math
import time

from cv2.typing import MatLike
from dummy_root import get_app_root
from roktracker.alliance.additional_data import AdditionalData
from roktracker.alliance.governor_data import GovernorData
from roktracker.alliance.governor_image_group import GovImageGroup
from roktracker.alliance.pandas_handler import PandasHandler
from roktracker.seed.ui_settings import KingdomUI
from roktracker.utils.adb import *
from roktracker.utils.general import *
from roktracker.utils.ocr import *
from roktracker.utils.output_formats import OutputFormats
from tesserocr import PyTessBaseAPI, PSM, OEM  # type: ignore
from typing import Callable, List


def default_batch_callback(govs: List[GovernorData], extra: AdditionalData) -> None:
    pass


def default_state_callback(msg: str) -> None:
    pass


def default_output_handler(msg: str) -> None:
    console.log(msg)
    pass


class SeedScanner:
    def __init__(self, port, config):
        self.run_id = generate_random_id(8)
        self.start_date = datetime.date.today()
        self.stop_scan = False
        self.scan_times = []

        self.reached_bottom = False
        self.govs_per_screen = 6
        self.screens_needed = 0

        # TODO: Load paths from config
        self.root_dir = get_app_root()
        self.tesseract_path = Path(self.root_dir / "deps" / "tessdata")
        self.img_path = Path(self.root_dir / "temp_images")
        self.img_path.mkdir(parents=True, exist_ok=True)
        self.scan_path = Path(self.root_dir / "scans_seed")
        self.scan_path.mkdir(parents=True, exist_ok=True)

        self.batch_callback = default_batch_callback
        self.state_callback = default_state_callback
        self.output_handler = default_output_handler

        self.adb_client = AdvancedAdbClient(
            str(self.root_dir / "deps" / "platform-tools" / "adb.exe"),
            port,
            config["general"]["emulator"],
            self.root_dir / "deps" / "inputs",
        )

    def set_batch_callback(
        self, cb: Callable[[List[GovernorData], AdditionalData], None]
    ) -> None:
        self.batch_callback = cb

    def set_state_callback(self, cb: Callable[[str], None]):
        self.state_callback = cb

    def set_output_handler(self, cb: Callable[[str], None]):
        self.output_handler = cb

    def get_remaining_time(self, remaining_govs: int) -> float:
        return (sum(self.scan_times, start=0) / len(self.scan_times)) * remaining_govs

    def process_ranking_screen(self, image: MatLike, position: int) -> GovImageGroup:
        if not self.reached_bottom:
            # fmt: off
            gov_name_im = cropToRegion(image, KingdomUI.name_normal[position])
            gov_name_im_bw = preprocessImage(
                gov_name_im, 3, KingdomUI.misc.threshold,
                12, KingdomUI.misc.invert,
            )

            gov_name_im_bw_small = preprocessImage(
                gov_name_im, 1, KingdomUI.misc.threshold,
                4, KingdomUI.misc.invert,
            )

            gov_score_im = cropToRegion(image, KingdomUI.score_normal[position])
            gov_score_im_bw = preprocessImage(
                gov_score_im,3,KingdomUI.misc.threshold,
                12,KingdomUI.misc.invert,
            )
            # fmt: on
        else:
            # fmt: off
            gov_name_im = cropToRegion(image, KingdomUI.name_last[position])
            gov_name_im_bw = preprocessImage(
                gov_name_im,3,KingdomUI.misc.threshold,
                12,KingdomUI.misc.invert,
            )

            gov_name_im_bw_small = preprocessImage(
                gov_name_im, 1, KingdomUI.misc.threshold,
                4, KingdomUI.misc.invert,
            )

            gov_score_im = cropToRegion(image, KingdomUI.score_last[position])
            gov_score_im_bw = preprocessImage(
                gov_score_im,3,KingdomUI.misc.threshold,
                12,KingdomUI.misc.invert,
            )
            # fmt: on

        return GovImageGroup(gov_name_im_bw, gov_name_im_bw_small, gov_score_im_bw)

    def scan_screen(self, screen_number: int) -> List[GovernorData]:
        # Take screenshot to process
        self.adb_client.secure_adb_screencap().save(self.img_path / "currentState.png")
        image = load_cv2_img(self.img_path / "currentState.png", cv2.IMREAD_UNCHANGED)

        # Check for last screen in alliance mode
        with PyTessBaseAPI(
            path=str(self.tesseract_path), psm=PSM.SINGLE_WORD, oem=OEM.LSTM_ONLY
        ) as api:
            # fmt: off
            test_score_im = cropToRegion(image, KingdomUI.score_normal[0])
            test_score_im_bw = preprocessImage(
                test_score_im,3,KingdomUI.misc.threshold,
                12,KingdomUI.misc.invert,
            )
            # fmt: on

            api.SetImage(Image.fromarray(test_score_im_bw))  # type: ignore
            test_score = api.GetUTF8Text()
            test_score = re.sub("[^0-9]", "", test_score)

            if test_score == "":
                self.reached_bottom = True

        # Actual scanning
        govs = []
        with PyTessBaseAPI(
            path=str(self.tesseract_path), psm=PSM.SINGLE_LINE, oem=OEM.LSTM_ONLY
        ) as api:
            for gov_number in range(0, self.govs_per_screen):
                gov = self.process_ranking_screen(image, gov_number)
                api.SetPageSegMode(PSM.SINGLE_LINE)
                gov_name = ocr_text(api, gov.name_img)

                api.SetPageSegMode(PSM.SINGLE_WORD)
                gov_score = ocr_number(api, gov.score_img)

                # fmt: off
                gov_img_path = str(self.img_path / f"gov_name_{(6 * screen_number) + gov_number}.png")
                # fmt: on
                write_cv2_img(
                    gov.name_img_small,
                    gov_img_path,
                    "png",
                )

                govs.append(GovernorData(gov_img_path, gov_name, gov_score))

        return govs

    def start_scan(self, kingdom: str, amount: int, formats: OutputFormats):
        self.state_callback("Initializing")
        self.adb_client.start_adb()
        self.screens_needed = int(math.ceil(amount / self.govs_per_screen))

        filename = f"Seed{amount}-{self.start_date}-{kingdom}-[{self.run_id}]"
        data_handler = PandasHandler(self.scan_path, filename, formats)

        self.state_callback("Scanning")

        for i in range(0, self.screens_needed):
            if self.stop_scan:
                self.output_handler("Scan Terminated! Saving the current progress...")
                break

            start_time = time.time()
            governors = self.scan_screen(i)
            end_time = time.time()

            self.scan_times.append(end_time - start_time)

            additional_data = AdditionalData(
                i,
                amount,
                self.govs_per_screen,
                self.get_remaining_time(self.screens_needed - i),
            )

            self.batch_callback(governors, additional_data)

            self.reached_bottom = (
                data_handler.write_governors(governors) or self.reached_bottom
            )
            data_handler.save()

            if self.reached_bottom:
                break
            else:
                self.adb_client.adb_send_events("Touch", KingdomUI.misc.script)
                time.sleep(1 + random.random())

        data_handler.save(amount, True)
        self.adb_client.kill_adb()  # make sure to clean up adb server

        for p in self.img_path.glob("gov_name*.png"):
            p.unlink()

        self.state_callback("Scan finished")

        return

    def end_scan(self) -> None:
        self.stop_scan = True
