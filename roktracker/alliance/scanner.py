import math
import time

from cv2.typing import MatLike
from dummy_root import get_app_root
from roktracker.alliance.additional_data import AdditionalData
from roktracker.alliance.excel_handler import ExcelHandler
from roktracker.alliance.governor_data import GovernorData
from roktracker.alliance.governor_image_group import GovImageGroup
from roktracker.utils.adb import *
from roktracker.utils.alliance_mode import mode_data
from roktracker.utils.general import *
from roktracker.utils.ocr import *
from tesserocr import PyTessBaseAPI, PSM, OEM  # type: ignore
from typing import Callable, List


def default_batch_callback(govs: List[GovernorData], extra: AdditionalData) -> None:
    pass


def default_output_handler(msg: str) -> None:
    console.log(msg)
    pass


class AllianceScanner:
    def __init__(self, port):
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
        self.scan_path = Path(self.root_dir / "scans_alliance")
        self.scan_path.mkdir(parents=True, exist_ok=True)

        self.batch_callback = default_batch_callback
        self.output_handler = default_output_handler

        self.adb_client = AdvancedAdbClient(
            str(self.root_dir / "deps" / "platform-tools" / "adb.exe"), port
        )

    def set_batch_callback(
        self, cb: Callable[[List[GovernorData], AdditionalData], None]
    ) -> None:
        self.batch_callback = cb

    def set_output_handler(self, cb: Callable[[str], None]):
        self.output_handler = cb

    def get_remaining_time(self, remaining_govs: int) -> float:
        return (sum(self.scan_times, start=0) / len(self.scan_times)) * remaining_govs

    def process_alliance_screen(self, image: MatLike, position: int) -> GovImageGroup:
        if not self.reached_bottom:
            # fmt: off
            gov_name_im = cropToRegion(image, mode_data["alliance"]["normal"]["name_pos"][position])
            gov_name_im_bw = preprocessImage(
                gov_name_im,3,mode_data["alliance"]["threshold"],
                12,mode_data["alliance"]["invert"],
            )

            gov_name_im_bw_small = preprocessImage(
                gov_name_im, 1, mode_data["alliance"]["threshold"],
                4, mode_data["alliance"]["invert"],
            )

            gov_score_im = cropToRegion(image, mode_data["alliance"]["normal"]["score_pos"][position])
            gov_score_im_bw = preprocessImage(
                gov_score_im,3,mode_data["alliance"]["threshold"],
                12,mode_data["alliance"]["invert"],
            )
            # fmt: on
        else:
            # fmt: off
            gov_name_im = cropToRegion(image, mode_data["alliance"]["last"]["name_pos"][position])
            gov_name_im_bw = preprocessImage(
                gov_name_im,3,mode_data["alliance"]["threshold"],
                12,mode_data["alliance"]["invert"],
            )

            gov_name_im_bw_small = preprocessImage(
                gov_name_im, 1, mode_data["alliance"]["threshold"],
                4, mode_data["alliance"]["invert"],
            )

            gov_score_im = cropToRegion(image, mode_data["alliance"]["last"]["score_pos"][position])
            gov_score_im_bw = preprocessImage(
                gov_score_im,3,mode_data["alliance"]["threshold"],
                12,mode_data["alliance"]["invert"],
            )
            # fmt: on

        return GovImageGroup(gov_name_im_bw, gov_name_im_bw_small, gov_score_im_bw)

    def scan_screen(self, screen_number: int) -> List[GovernorData]:
        # Take screenshot to process
        self.adb_client.secure_adb_screencap().save(self.img_path / "currentState.png")
        image = cv2.imread(str(self.img_path / "currentState.png"))

        # Check for last screen in alliance mode
        with PyTessBaseAPI(
            path=str(self.tesseract_path), psm=PSM.SINGLE_WORD, oem=OEM.LSTM_ONLY
        ) as api:
            # fmt: off
            test_score_im = cropToRegion(image, mode_data["alliance"]["normal"]["score_pos"][0])
            test_score_im_bw = preprocessImage(
                test_score_im,3,mode_data["alliance"]["threshold"],
                12,mode_data["alliance"]["invert"],
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
                gov = self.process_alliance_screen(image, gov_number)
                api.SetPageSegMode(PSM.SINGLE_LINE)
                gov_name = ocr_text(api, gov.name_img)

                api.SetPageSegMode(PSM.SINGLE_WORD)
                gov_score = ocr_number(api, gov.score_img)

                # fmt: off
                gov_img_path = str(self.img_path / f"gov_name_{(6 * screen_number) + 1}.png")
                cv2.imwrite(gov_img_path, gov.name_img_small)
                # fmt: on

                govs.append(GovernorData(gov_img_path, gov_name, gov_score))

        return govs

    def start_scan(self, kingdom: str, amount: int):
        self.screens_needed = int(math.ceil(amount / self.govs_per_screen))

        filename = f"Alliance{amount}-{self.start_date}-{kingdom}-[{self.run_id}].xlsx"

        ######Excel Formatting
        excel = ExcelHandler(
            str(self.scan_path / filename),
            self.start_date,
        )

        for i in range(0, self.screens_needed):
            if self.stop_scan:
                self.output_handler("Scan Terminated! Saving the current progress...")
                break

            start_time = time.time()
            governors = self.scan_screen(i)

            self.adb_client.adb_send_events("Touch", mode_data["alliance"]["script"])
            time.sleep(1 + random.random())

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
                excel.add_results_to_sheet(governors, i) or self.reached_bottom
            )
            excel.save()

            if self.reached_bottom:
                break

        excel.save()
        self.adb_client.kill_adb()  # make sure to clean up adb server

        for p in self.img_path.glob("gov_name*.png"):
            p.unlink()

        return

    def end_scan(self) -> None:
        self.stop_scan = True
