import sys

required_version = (
    3,
    11,
)  # Replace with the required version tuple, e.g., (3, 9) for Python 3.9
current_version = sys.version_info

if current_version < required_version:
    print(
        f"Update required: Current Python version is {current_version.major}.{current_version.minor} "
        f"but version {required_version[0]}.{required_version[1]} or higher is needed."
    )
    sys.exit(1)

from console import console
from adbutils import *
from rich.console import Console
from rich.table import Table
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.drawing.image import Image as OpImage
from pathlib import Path
from tesserocr import PyTessBaseAPI, PSM, OEM
from PIL import Image
from validator import validate_installation
import configparser
import datetime
import time
import random
import cv2
import signal
import re
import json
import math
import questionary
import string

# this is needed due to not yet published fix from InquirerPy
# pyright: reportPrivateImportUsage=false

if getattr(sys, "frozen", False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    print("Bundle detected!")
    root_dir = Path(sys.executable).parent
else:
    root_dir = Path(__file__).parent

config_file = open(root_dir / "config.json")
config = json.load(config_file)
config_file.close()

img_path = Path(root_dir / "temp_images")
img_path.mkdir(parents=True, exist_ok=True)
tesseract_path = Path(root_dir / "deps" / "tessdata")

scan_path = Path(root_dir / "scans_alliance")
scan_path.mkdir(parents=True, exist_ok=True)

set_adb_path(str(root_dir / "deps" / "platform-tools" / "adb.exe"))

console = Console()
scan_index = 0
reached_bottom = False
abort_scan = False
run_id = ""
start_date = ""
scan_times = []

mode_data = {
    "alliance": {
        "name": (334, 260, 293, 33),
        "score": (1117, 265, 250, 33),
        "threshold": 90,
        "invert": True,
        "script": str(root_dir / "deps/inputs/alliance_6_person_scroll.txt"),
        "normal": {
            "name_pos": [
                (334, 260, 293, 33),
                (334, 359, 293, 33),
                (334, 460, 293, 33),
                (334, 562, 293, 33),
                (334, 662, 293, 33),
                (334, 763, 293, 33),
            ],
            "score_pos": [
                (1117, 265, 250, 33),
                (1117, 364, 250, 33),
                (1117, 465, 250, 33),
                (1117, 567, 250, 33),
                (1117, 667, 250, 33),
                (1117, 768, 250, 33),
            ],
        },
        "last": {
            "name_pos": [
                (334, 283, 293, 33),
                (334, 383, 293, 33),
                (334, 483, 293, 33),
                (334, 595, 293, 33),
                (334, 685, 293, 33),
                (334, 785, 293, 33),
            ],
            "score_pos": [
                (1117, 288, 250, 33),
                (1117, 388, 250, 33),
                (1117, 488, 250, 33),
                (1117, 590, 250, 33),
                (1117, 690, 250, 33),
                (1117, 790, 250, 33),
            ],
        },
    },
    "honor": {
        "name": (774, 330, 257, 33),
        "score": (1183, 330, 178, 33),
        "threshold": 150,
        "invert": False,
        "script": str(root_dir / "deps/inputs/honor_5_person_scroll.txt"),
        "name_pos": [
            (774, 324, 257, 40),
            (774, 424, 257, 40),
            (774, 524, 257, 40),
            (774, 624, 257, 40),
            (774, 724, 257, 40),
        ],
        "score_pos": [
            (1183, 324, 178, 40),
            (1183, 424, 178, 40),
            (1183, 524, 178, 40),
            (1183, 624, 178, 40),
            (1183, 724, 178, 40),
        ],
    },
}


def get_bluestacks_port(bluestacks_device_name):
    # try to read port from bluestacks config
    try:
        dummy = "AmazingDummy"
        with open(config["general"]["bluestacks_config"]) as config_file:
            file_content = "[" + dummy + "]\n" + config_file.read()
        bluestacks_config = configparser.RawConfigParser()
        bluestacks_config.read_string(file_content)

        for key, value in bluestacks_config.items(dummy):
            if value == f'"{bluestacks_device_name}"':
                key_port = key.replace("display_name", "status.adb_port")
                port = bluestacks_config.get(dummy, key_port)
                return int(port.strip('"'))
    except:
        console.print(
            "[red]Could not parse or find bluestacks config. Defaulting to 5555.[/red]"
        )
        return 5555
    return 5555


def to_int_check(element):
    try:
        return int(element)
    except ValueError:
        # return element
        return int(0)


def stopHandler(signum, frame):
    global abort_scan
    stop = questionary.confirm(
        message="Do you want to stop the scanner?:", auto_enter=False, default=False
    ).ask()
    if stop:
        console.print("Scan will aborted after next governor.")
        abort_scan = True


def get_remaining_time(remaining_govs: int) -> float:
    return (sum(scan_times, start=0) / len(scan_times)) * remaining_govs


def cropToRegion(image, roi):
    return image[int(roi[1]) : int(roi[1] + roi[3]), int(roi[0]) : int(roi[0] + roi[2])]


def cropToTextWithBorder(img, border_size):
    coords = cv2.findNonZero(cv2.bitwise_not(img))
    x, y, w, h = cv2.boundingRect(coords)

    roi = img[y : y + h, x : x + w]
    bordered = cv2.copyMakeBorder(
        roi,
        top=border_size,
        bottom=border_size,
        left=border_size,
        right=border_size,
        borderType=cv2.BORDER_CONSTANT,
        value=255,
    )

    return bordered


def preprocessImage(image, scale_factor, threshold, border_size, invert=False):
    im_big = cv2.resize(image, (0, 0), fx=scale_factor, fy=scale_factor)
    im_gray = cv2.cvtColor(im_big, cv2.COLOR_BGR2GRAY)
    if invert:
        im_gray = cv2.bitwise_not(im_gray)
    (thresh, im_bw) = cv2.threshold(im_gray, threshold, 255, cv2.THRESH_BINARY)
    im_bw = cropToTextWithBorder(im_bw, border_size)
    return im_bw


def is_string_int(element: str) -> bool:
    try:
        _ = int(element)
        return True
    except ValueError:
        return False


def print_results(
    governors, current_time, amount, current_screen, total_screens, govs_per_screen
):
    # nice output for console
    table = Table(
        title="["
        + current_time
        + "]\n"
        + "Latest Scan Result\nGovernor "
        + f"{current_screen * govs_per_screen} - {current_screen * govs_per_screen + len(governors)}"
        + " of "
        + str(amount),
        show_header=True,
        show_footer=True,
    )
    table.add_column("Governor Name", "Approx time remaining\nSkipped", style="magenta")
    table.add_column(
        "Score", str(get_remaining_time(total_screens - current_screen)), style="cyan"
    )

    for governor in governors:
        table.add_row(governor["name"], str(governor["score"]))

    console.print(table)


def check_for_duplicate(governor, sheet, governor_number):
    for row in sheet.iter_rows(
        min_col=2,
        max_col=3,
        min_row=max(2, governor_number - 5),
        max_row=governor_number + 1,
    ):
        if row[0].value == governor["name"] and row[1].value == to_int_check(
            governor["score"]
        ):
            return True
    return False


def add_results_to_sheet(governors, sheet, screen_number):
    global reached_bottom
    govs_per_screen = len(governors)
    duplicates = 0
    for gov_num, governor in enumerate(governors):
        current_gov = (govs_per_screen * screen_number) + gov_num - duplicates

        if check_for_duplicate(governor, sheet, current_gov):
            print(f"Removed duplicated governor ({governor['name']}).")
            duplicates += 1
            # Duplicate can only happen on the last page
            reached_bottom = True
            continue

        sheet.row_dimensions[current_gov + 2].height = 24.75
        # Write results in excel file
        sheet.add_image(
            OpImage(
                str(
                    img_path
                    / ("gov_name_" + str(current_gov + 1 + duplicates) + ".png")
                )
            ),
            "A" + str(current_gov + 2),
        )
        sheet["B" + str(current_gov + 2)] = governor["name"]
        sheet["C" + str(current_gov + 2)] = to_int_check(governor["score"])


def process_alliance_screen(image, position):
    global reached_bottom

    if not reached_bottom:
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

    return (gov_name_im_bw, gov_name_im_bw_small, gov_score_im_bw)


def process_honor_screen(image, position):
    # fmt: off
    gov_name_im = cropToRegion(image, mode_data["honor"]["name_pos"][position])
    gov_name_im_bw = preprocessImage(
        gov_name_im,3,mode_data["honor"]["threshold"],
        12,mode_data["honor"]["invert"],
    )

    gov_name_im_bw_small = preprocessImage(
        gov_name_im, 1, mode_data["honor"]["threshold"],
        4, mode_data["honor"]["invert"],
    )

    gov_score_im = cropToRegion(image, mode_data["honor"]["score_pos"][position])
    gov_score_im_bw = preprocessImage(
        gov_score_im,3,mode_data["honor"]["threshold"],
        12,mode_data["honor"]["invert"],
    )
    # fmt: on

    return (gov_name_im_bw, gov_name_im_bw_small, gov_score_im_bw)


def generate_random_id(length):
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choices(alphabet, k=length))


def ocr_score(api, image):
    api.SetImage(Image.fromarray(image))
    score = api.GetUTF8Text()
    score = re.sub("[^0-9]", "", score)
    return score


def ocr_name(api, image):
    api.SetImage(Image.fromarray(image))
    name = api.GetUTF8Text()
    return name.rstrip("\n")


def scan_screen(mode: str, port: int, screen_number: int):
    # set up the scan variables
    global scan_index
    global reached_bottom
    gov_name = ""
    gov_score = 0

    # Take screenshot to process
    secure_adb_screencap(port).save(img_path / "currentState.png")
    image = cv2.imread(str(img_path / "currentState.png"))

    # Check for last screen in alliance mode
    if mode == "alliance":
        with PyTessBaseAPI(
            path=str(tesseract_path), psm=PSM.SINGLE_WORD, oem=OEM.LSTM_ONLY
        ) as api:
            # fmt: off
            test_score_im = cropToRegion(image, mode_data[mode]["normal"]["score_pos"][0])
            test_score_im_bw = preprocessImage(
                test_score_im,3,mode_data[mode]["threshold"],
                12,mode_data[mode]["invert"],
            )
            # fmt: on

            api.SetImage(Image.fromarray(test_score_im_bw))
            test_score = api.GetUTF8Text()
            test_score = re.sub("[^0-9]", "", test_score)

            if test_score == "":
                reached_bottom = True

    # Actual scanning
    if mode == "alliance":
        (
            gov_1_name_im_bw,
            gov_1_name_im_bw_small,
            gov_1_score_im_bw,
        ) = process_alliance_screen(image, 0)

        (
            gov_2_name_im_bw,
            gov_2_name_im_bw_small,
            gov_2_score_im_bw,
        ) = process_alliance_screen(image, 1)

        (
            gov_3_name_im_bw,
            gov_3_name_im_bw_small,
            gov_3_score_im_bw,
        ) = process_alliance_screen(image, 2)

        (
            gov_4_name_im_bw,
            gov_4_name_im_bw_small,
            gov_4_score_im_bw,
        ) = process_alliance_screen(image, 3)

        (
            gov_5_name_im_bw,
            gov_5_name_im_bw_small,
            gov_5_score_im_bw,
        ) = process_alliance_screen(image, 4)

        (
            gov_6_name_im_bw,
            gov_6_name_im_bw_small,
            gov_6_score_im_bw,
        ) = process_alliance_screen(image, 5)

        with PyTessBaseAPI(
            path=str(tesseract_path), psm=PSM.SINGLE_LINE, oem=OEM.LSTM_ONLY
        ) as api:
            gov_1_name = ocr_name(api, gov_1_name_im_bw)
            gov_2_name = ocr_name(api, gov_2_name_im_bw)
            gov_3_name = ocr_name(api, gov_3_name_im_bw)
            gov_4_name = ocr_name(api, gov_4_name_im_bw)
            gov_5_name = ocr_name(api, gov_5_name_im_bw)
            gov_6_name = ocr_name(api, gov_6_name_im_bw)

            # fmt: off
            cv2.imwrite(str(img_path / f"gov_name_{(6 * screen_number) + 1}.png"), gov_1_name_im_bw_small)
            cv2.imwrite(str(img_path / f"gov_name_{(6 * screen_number) + 2}.png"), gov_2_name_im_bw_small)
            cv2.imwrite(str(img_path / f"gov_name_{(6 * screen_number) + 3}.png"), gov_3_name_im_bw_small)
            cv2.imwrite(str(img_path / f"gov_name_{(6 * screen_number) + 4}.png"), gov_4_name_im_bw_small)
            cv2.imwrite(str(img_path / f"gov_name_{(6 * screen_number) + 5}.png"), gov_5_name_im_bw_small)
            cv2.imwrite(str(img_path / f"gov_name_{(6 * screen_number) + 6}.png"), gov_6_name_im_bw_small)
            # fmt: on

            api.SetPageSegMode(PSM.SINGLE_WORD)
            gov_1_score = ocr_score(api, gov_1_score_im_bw)
            gov_2_score = ocr_score(api, gov_2_score_im_bw)
            gov_3_score = ocr_score(api, gov_3_score_im_bw)
            gov_4_score = ocr_score(api, gov_4_score_im_bw)
            gov_5_score = ocr_score(api, gov_5_score_im_bw)
            gov_6_score = ocr_score(api, gov_6_score_im_bw)

        return [
            {"name": gov_1_name, "score": gov_1_score},
            {"name": gov_2_name, "score": gov_2_score},
            {"name": gov_3_name, "score": gov_3_score},
            {"name": gov_4_name, "score": gov_4_score},
            {"name": gov_5_name, "score": gov_5_score},
            {"name": gov_6_name, "score": gov_6_score},
        ]

    elif mode == "honor":
        (
            gov_1_name_im_bw,
            gov_1_name_im_bw_small,
            gov_1_score_im_bw,
        ) = process_honor_screen(image, 0)

        (
            gov_2_name_im_bw,
            gov_2_name_im_bw_small,
            gov_2_score_im_bw,
        ) = process_honor_screen(image, 1)

        (
            gov_3_name_im_bw,
            gov_3_name_im_bw_small,
            gov_3_score_im_bw,
        ) = process_honor_screen(image, 2)

        (
            gov_4_name_im_bw,
            gov_4_name_im_bw_small,
            gov_4_score_im_bw,
        ) = process_honor_screen(image, 3)

        (
            gov_5_name_im_bw,
            gov_5_name_im_bw_small,
            gov_5_score_im_bw,
        ) = process_honor_screen(image, 4)

        with PyTessBaseAPI(
            path=str(tesseract_path), psm=PSM.SINGLE_LINE, oem=OEM.LSTM_ONLY
        ) as api:
            gov_1_name = ocr_name(api, gov_1_name_im_bw)
            gov_2_name = ocr_name(api, gov_2_name_im_bw)
            gov_3_name = ocr_name(api, gov_3_name_im_bw)
            gov_4_name = ocr_name(api, gov_4_name_im_bw)
            gov_5_name = ocr_name(api, gov_5_name_im_bw)

            # fmt: off
            cv2.imwrite(str(img_path / f"gov_name_{(5 * screen_number) + 1}.png"), gov_1_name_im_bw_small)
            cv2.imwrite(str(img_path / f"gov_name_{(5 * screen_number) + 2}.png"), gov_2_name_im_bw_small)
            cv2.imwrite(str(img_path / f"gov_name_{(5 * screen_number) + 3}.png"), gov_3_name_im_bw_small)
            cv2.imwrite(str(img_path / f"gov_name_{(5 * screen_number) + 4}.png"), gov_4_name_im_bw_small)
            cv2.imwrite(str(img_path / f"gov_name_{(5 * screen_number) + 5}.png"), gov_5_name_im_bw_small)
            # fmt: on

            api.SetPageSegMode(PSM.SINGLE_WORD)
            gov_1_score = ocr_score(api, gov_1_score_im_bw)
            gov_2_score = ocr_score(api, gov_2_score_im_bw)
            gov_3_score = ocr_score(api, gov_3_score_im_bw)
            gov_4_score = ocr_score(api, gov_4_score_im_bw)
            gov_5_score = ocr_score(api, gov_5_score_im_bw)

        return [
            {"name": gov_1_name, "score": gov_1_score},
            {"name": gov_2_name, "score": gov_2_score},
            {"name": gov_3_name, "score": gov_3_score},
            {"name": gov_4_name, "score": gov_4_score},
            {"name": gov_5_name, "score": gov_5_score},
        ]

    else:
        return []


def fast_scan(port: int, kingdom: str, mode: str, amount: int):
    govs_per_screen = 1

    if mode == "alliance":
        screen_amount = int(math.ceil(amount / 6))
        govs_per_screen = 6
    else:
        screen_amount = int(math.ceil(amount / 5))
        govs_per_screen = 5

    # Initialize the connection to adb
    device = start_adb(port)

    ######Excel Formatting
    wb = Workbook()
    sheet1 = wb.active
    sheet1.title = str(datetime.date.today())

    # Make Head Bold
    font = Font(bold=True)

    # Initialize Excel Sheet Header
    sheet1["A1"] = "Name Image"
    sheet1["B1"] = "Governor Name"
    sheet1["C1"] = "Governor Score"

    sheet1.column_dimensions["A"].width = 42
    sheet1["A1"].font = font
    sheet1["B1"].font = font
    sheet1["C1"].font = font

    stop = False

    for i in range(0, screen_amount):
        if abort_scan:
            console.print("Scan Terminated! Saving the current progress...")
            break

        start_time = time.time()
        governors = scan_screen(mode, port, i)

        adb_send_events("Touch", mode_data[mode]["script"], port)
        time.sleep(1 + random.random())

        end_time = time.time()
        scan_times.append(end_time - start_time)

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")

        print_results(
            governors, current_time, amount, i, screen_amount, govs_per_screen
        )

        add_results_to_sheet(governors, sheet1, i)

        if mode == "alliance":
            file_name_prefix = "ALLIANCE"
        else:
            file_name_prefix = "HONOR"
        wb.save(
            str(
                scan_path
                / (
                    file_name_prefix
                    + str(amount)
                    + "-"
                    + str(start_date)
                    + "-"
                    + kingdom
                    + f"-[{run_id}]"
                    + ".xlsx"
                )
            )
        )

        # if not reached_bottom:

        if reached_bottom:
            break

    if mode == "alliance":
        file_name_prefix = "ALLIANCE"
    else:
        file_name_prefix = "HONOR"
    wb.save(
        str(
            scan_path
            / (
                file_name_prefix
                + str(amount)
                + "-"
                + str(start_date)
                + "-"
                + kingdom
                + f"-[{run_id}]"
                + ".xlsx"
            )
        )
    )
    kill_adb()  # make sure to clean up adb server

    for p in img_path.glob("gov_name*.png"):
        p.unlink()

    return


def main():
    if not validate_installation():
        exit(2)
    signal.signal(signal.SIGINT, stopHandler)

    global run_id
    global start_date

    run_id = generate_random_id(8)
    start_date = datetime.date.today()
    console.print(f"The UUID of this scan is [green]{run_id}[/green]", highlight=False)

    bluestacks_device_name = questionary.text(
        message="Name of your bluestacks instance:",
        default=config["general"]["bluestacks_name"],
    ).ask()

    bluestacks_port = int(
        questionary.text(
            f"Adb port of device (detected {get_bluestacks_port(bluestacks_device_name)}):",
            default=str(get_bluestacks_port(bluestacks_device_name)),
            validate=lambda port: is_string_int(port),
        ).ask()
    )

    kingdom = questionary.text(
        message="Kingdom name (used for file name):",
        default=config["scan"]["kingdom_name"],
    ).ask()

    scan_amount = int(
        questionary.text(
            message="Number of people to scan:",
            validate=lambda port: is_string_int(port),
            default=str(config["scan"]["people_to_scan"]),
        ).ask()
    )

    scan_mode = questionary.select(
        "What do you want to scan?",
        choices=[
            questionary.Choice(
                "Alliance",
                value="alliance",
                checked=True,
                shortcut_key="f",
            ),
            questionary.Choice(
                "Honor",
                value="honor",
                checked=False,
                shortcut_key="s",
            ),
        ],
    ).ask()

    fast_scan(int(bluestacks_port), kingdom, scan_mode, int(scan_amount))

    exit(1)


if __name__ == "__main__":
    main()
