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
from rich.table import Table
from rich.markup import escape
from openpyxl import Workbook
from openpyxl.styles import Font
from pathlib import Path
from adbutils import *
import questionary
import tkinter
import configparser
import datetime
import time
import random
import cv2
import signal
import re
import logging
import math
import shutil
import string
import time
import tesserocr
import rok_ui_positions as rok_ui
from tesserocr import PyTessBaseAPI, PSM, OEM
from PIL import Image

logging.basicConfig(
    filename="rok-scanner.log",
    encoding="utf-8",
    format="%(asctime)s %(module)s %(levelname)s %(message)s",
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
)

run_id = ""
start_date = ""
new_scroll = True
scan_abort = False
scan_times = []

scan_options = {
    "ID": False,
    "Name": False,
    "Power": False,
    "Killpoints": False,
    "Alliance": False,
    "T1 Kills": False,
    "T2 Kills": False,
    "T3 Kills": False,
    "T4 Kills": False,
    "T5 Kills": False,
    "Ranged": False,
    "Deads": False,
    "Rss Assistance": False,
    "Rss Gathered": False,
    "Helps": False,
}


def format_timedelta_to_HHMMSS(td):
    td_in_seconds = td.total_seconds()
    hours, remainder = divmod(td_in_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    if minutes < 10:
        minutes = "0{}".format(minutes)
    if seconds < 10:
        seconds = "0{}".format(seconds)
    return "{}:{}:{}".format(hours, minutes, seconds)


def next_alpha(s):
    return chr((ord(s.upper()) + 1 - 65) % 26 + 65)


def random_delay() -> float:
    return random.random() * 0.1


def get_remaining_time(remaining_govs: int) -> float:
    return (sum(scan_times, start=0) / len(scan_times)) * remaining_govs


def get_bluestacks_port(bluestacks_device_name):
    # try to read port from bluestacks config
    try:
        dummy = "AmazingDummy"
        with open(
            "S:\\Other\\BlueStacks\\BlueStacks_nxt\\bluestacks.conf"
        ) as config_file:
            file_content = "[" + dummy + "]\n" + config_file.read()
        config = configparser.RawConfigParser()
        config.read_string(file_content)

        for key, value in config.items(dummy):
            if value == f'"{bluestacks_device_name}"':
                key_port = key.replace("display_name", "status.adb_port")
                port = config.get(dummy, key_port)
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


def is_string_int(element: str) -> bool:
    try:
        _ = int(element)
        return True
    except ValueError:
        return False


def generate_random_id(length):
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choices(alphabet, k=length))


def get_gov_position(current_position, skips):
    # Positions for next governor to check
    Y = [285, 390, 490, 590, 605, 705, 805]

    # skips only are relevant in the first 4 governors
    if current_position + skips < 4:
        return Y[current_position + skips]
    else:
        if current_position < 998:
            return Y[4]
        elif current_position == 998:
            return Y[5]
        elif current_position == 999:
            return Y[6]
        else:
            console.log("Reached final governor on the screen. Scan complete.")
            logging.log(
                logging.INFO, "Reached final governor on the screen. Scan complete."
            )
            exit(0)


def stopHandler(signum, frame):
    global scan_abort
    stop = questionary.confirm(
        message="Do you want to stop the scanner?:", auto_enter=False, default=False
    ).ask()
    if stop:
        console.print("Scan will aborted after next governor.")
        scan_abort = True


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


def preprocessImage(image, threshold, border_size, invert=False):
    im_big = cv2.resize(image, (0, 0), fx=3, fy=3)
    im_gray = cv2.cvtColor(im_big, cv2.COLOR_BGR2GRAY)
    if invert:
        im_gray = cv2.bitwise_not(im_gray)
    (thresh, im_bw) = cv2.threshold(im_gray, threshold, 255, cv2.THRESH_BINARY)
    im_bw = cropToTextWithBorder(im_bw, border_size)
    return im_bw


def are_kills_ok(kills_t1, kills_t2, kills_t3, kills_t4, kills_t5, kill_points) -> bool:
    expectedKp = (
        math.floor(kills_t1 * 0.2)
        + (kills_t2 * 2)
        + (kills_t3 * 4)
        + (kills_t4 * 10)
        + (kills_t5 * 20)
    )
    return expectedKp == kill_points


def are_kp_ok(kp_t1, kp_t2, kp_t3, kp_t4, kp_t5, kill_points) -> bool:
    expectedKp = kp_t1 + kp_t2 + kp_t3 + kp_t4 + kp_t5
    return kill_points == expectedKp


def calculate_kills(
    k_t1: int, kp_t1: int, kp_t2: int, kp_t3: int, kp_t4: int, kp_t5: int
) -> tuple[int, int, int, int, int]:
    kills_t1 = kp_t1 / 0.2

    if kills_t1 < k_t1 <= (kills_t1 + 4):  # fix t1 kills if no error is present
        kills_t1 = k_t1
    elif (
        kills_t1 % 10 < k_t1 % 10 <= (kills_t1 + 4) % 10
    ):  # try to fix t1 with error (assuming last digit is correct)
        kill_dif_t1 = (k_t1 % 10) - (kills_t1 % 10)
        kills_t1 = kills_t1 + kill_dif_t1

    kills_t2 = kp_t2 / 2
    kills_t3 = kp_t3 / 4
    kills_t4 = kp_t4 / 10
    kills_t5 = kp_t5 / 20
    return int(kills_t1), int(kills_t2), int(kills_t3), int(kills_t4), int(kills_t5)


def check_page_needed(page: int) -> bool:
    match page:
        case 1:
            return (
                scan_options["ID"]
                or scan_options["Name"]
                or scan_options["Power"]
                or scan_options["Killpoints"]
                or scan_options["Alliance"]
            )
        case 2:
            return (
                scan_options["T1 Kills"]
                or scan_options["T2 Kills"]
                or scan_options["T3 Kills"]
                or scan_options["T4 Kills"]
                or scan_options["T5 Kills"]
                or scan_options["Ranged"]
            )
        case 3:
            return (
                scan_options["Deads"]
                or scan_options["Rss Assistance"]
                or scan_options["Rss Gathered"]
                or scan_options["Helps"]
            )
        case _:
            return False


def assign_columns():
    assigned_cols = {}
    current_char = "A"

    if scan_options["ID"]:
        assigned_cols.update({"ID": current_char})
        current_char = next_alpha(current_char)

    if scan_options["Name"]:
        assigned_cols.update({"Name": current_char})
        current_char = next_alpha(current_char)

    if scan_options["Power"]:
        assigned_cols.update({"Power": current_char})
        current_char = next_alpha(current_char)

    if scan_options["Killpoints"]:
        assigned_cols.update({"Killpoints": current_char})
        current_char = next_alpha(current_char)

    if scan_options["Deads"]:
        assigned_cols.update({"Deads": current_char})
        current_char = next_alpha(current_char)

    if scan_options["T1 Kills"]:
        assigned_cols.update({"T1 Kills": current_char})
        current_char = next_alpha(current_char)

    if scan_options["T2 Kills"]:
        assigned_cols.update({"T2 Kills": current_char})
        current_char = next_alpha(current_char)

    if scan_options["T3 Kills"]:
        assigned_cols.update({"T3 Kills": current_char})
        current_char = next_alpha(current_char)

    if scan_options["T4 Kills"]:
        assigned_cols.update({"T4 Kills": current_char})
        current_char = next_alpha(current_char)

    if scan_options["T5 Kills"]:
        assigned_cols.update({"T5 Kills": current_char})
        current_char = next_alpha(current_char)

    if (
        scan_options["T1 Kills"]
        and scan_options["T2 Kills"]
        and scan_options["T3 Kills"]
        and scan_options["T4 Kills"]
        and scan_options["T5 Kills"]
    ):
        assigned_cols.update({"Total Kills": current_char})
        current_char = next_alpha(current_char)

    if scan_options["T4 Kills"] and scan_options["T5 Kills"]:
        assigned_cols.update({"T45 Kills": current_char})
        current_char = next_alpha(current_char)

    if scan_options["Ranged"]:
        assigned_cols.update({"Ranged": current_char})
        current_char = next_alpha(current_char)

    if scan_options["Rss Gathered"]:
        assigned_cols.update({"Rss Gathered": current_char})
        current_char = next_alpha(current_char)

    if scan_options["Rss Assistance"]:
        assigned_cols.update({"Rss Assistance": current_char})
        current_char = next_alpha(current_char)

    if scan_options["Helps"]:
        assigned_cols.update({"Helps": current_char})
        current_char = next_alpha(current_char)

    if scan_options["Alliance"]:
        assigned_cols.update({"Alliance": current_char})
        current_char = next_alpha(current_char)

    return assigned_cols


def createHeader(display_name, name, colNames, sheet, font):
    if name in colNames:
        sheet[str(colNames[name]) + "1"] = display_name
        sheet[str(colNames[name]) + "1"].font = font


def setCell(sheet, colNames, name, row, value):
    if name in colNames:
        sheet[str(colNames[name]) + str(row)] = value


def governor_scan(
    port: int,
    current_player: int,
    inactive_players: int,
    track_inactives: bool,
    state_callback=lambda _: (),
):
    start_time = time.time()
    # set up the scan variables
    gov_name = "Skipped"
    gov_id = "Skipped"
    gov_power = "Skipped"
    gov_killpoints = "Skipped"
    alliance_name = "Skipped"
    gov_kills_tier1 = "Skipped"
    gov_kp_tier1 = "Skipped"
    gov_kills_tier2 = "Skipped"
    gov_kp_tier2 = "Skipped"
    gov_kills_tier3 = "Skipped"
    gov_kp_tier3 = "Skipped"
    gov_kills_tier4 = "Skipped"
    gov_kp_tier4 = "Skipped"
    gov_kills_tier5 = "Skipped"
    gov_kp_tier5 = "Skipped"
    gov_ranged_points = "Skipped"
    gov_kills_tier45 = "Skipped"
    gov_kills_total = "Skipped"
    gov_dead = "Skipped"
    gov_rss_assistance = "Skipped"
    gov_rss_gathered = "Skipped"
    gov_helps = "Skipped"

    state_callback("Opening governor")
    # Open governor
    secure_adb_shell(
        f"input tap 690 " + str(get_gov_position(current_player, inactive_players)),
        port,
    )
    time.sleep(2 + random_delay())

    gov_info = False
    count = 0

    while not (gov_info):
        secure_adb_screencap(port).save("check_more_info.png")

        image_check = cv2.imread("check_more_info.png", cv2.IMREAD_GRAYSCALE)
        # Checking for more info
        im_check_more_info = cropToRegion(image_check, rok_ui.ocr_regions["more_info"])
        check_more_info = ""

        with PyTessBaseAPI(path="./deps/tessdata-main") as api:
            api.SetVariable("tessedit_char_whitelist", "MoreInfo")
            api.SetImage(Image.fromarray(im_check_more_info))
            check_more_info = api.GetUTF8Text()

        # Probably tapped governor is inactive and needs to be skipped
        if "MoreInfo" not in check_more_info:
            inactive_players += 1
            if track_inactives:
                image_check_inactive = cv2.imread("check_more_info.png")
                roiInactive = (
                    0,
                    get_gov_position(current_player, inactive_players - 1) - 100,
                    1400,
                    200,
                )
                image_inactive_raw = cropToRegion(image_check_inactive, roiInactive)
                cv2.imwrite(
                    f"./inactives/{start_date}/{run_id}/inactive {inactive_players:03}.png",
                    image_inactive_raw,
                )
            if new_scroll:
                adb_send_events("Touch", "./inputs/kingdom_1_person_scroll.txt", port)
            else:
                secure_adb_shell(f"input swipe 690 605 690 540", port)
            secure_adb_shell(
                f"input tap 690 "
                + str(get_gov_position(current_player, inactive_players)),
                port,
            )
            count += 1
            time.sleep(2 + random_delay())
            if count == 10:
                cont = questionary.confirm(
                    message="Could not find user, retry?:",
                    auto_enter=False,
                    default=True,
                ).ask()
                if cont:
                    count = 0
                else:
                    break
        else:
            gov_info = True
            break

    if check_page_needed(1):
        state_callback("Scanning general page")
        if scan_options["Name"]:
            # nickname copy
            copy_try = 0
            while copy_try < 3:
                try:
                    secure_adb_tap(rok_ui.tap_positions["name_copy"], port)
                    time.sleep(0.2)
                    gov_name = tkinter.Tk().clipboard_get()
                    break
                except:
                    console.log("Name copy failed, retying")
                    logging.log(logging.INFO, "Name copy failed, retying")
                    copy_try = copy_try + 1

        time.sleep(1.5 + random_delay())

        secure_adb_screencap(port).save("gov_info.png")
        image = cv2.imread("gov_info.png")

        # 1st image data (ID, Power, Killpoints, Alliance)
        with PyTessBaseAPI(
            path="./deps/tessdata-main", psm=PSM.SINGLE_WORD, oem=OEM.LSTM_ONLY
        ) as api:
            if scan_options["Power"]:
                im_gov_power = cropToRegion(image, rok_ui.ocr_regions["power"])
                im_gov_power_bw = preprocessImage(im_gov_power, 100, 12, True)

                api.SetImage(Image.fromarray(im_gov_power_bw))
                gov_power = api.GetUTF8Text()
                gov_power = re.sub("[^0-9]", "", gov_power)

            if scan_options["Killpoints"]:
                im_gov_killpoints = cropToRegion(
                    image, rok_ui.ocr_regions["killpoints"]
                )
                im_gov_killpoints_bw = preprocessImage(im_gov_killpoints, 100, 12, True)

                api.SetImage(Image.fromarray(im_gov_killpoints_bw))
                gov_killpoints = api.GetUTF8Text()
                gov_killpoints = re.sub("[^0-9]", "", gov_killpoints)

            api.SetPageSegMode(PSM.SINGLE_LINE)
            if scan_options["ID"]:
                im_gov_id = cropToRegion(image, rok_ui.ocr_regions["gov_id"])
                im_gov_id_gray = cv2.cvtColor(im_gov_id, cv2.COLOR_BGR2GRAY)
                im_gov_id_gray = cv2.bitwise_not(im_gov_id_gray)
                (thresh, im_gov_id_bw) = cv2.threshold(
                    im_gov_id_gray, 120, 255, cv2.THRESH_BINARY
                )

                api.SetImage(Image.fromarray(im_gov_id_bw))
                gov_id = api.GetUTF8Text()
                gov_id = re.sub("[^0-9]", "", gov_id)

            if scan_options["Alliance"]:
                im_alliance_tag = cropToRegion(
                    image, rok_ui.ocr_regions["alliance_name"]
                )
                im_alliance_bw = preprocessImage(im_alliance_tag, 50, 12, True)

                api.SetImage(Image.fromarray(im_alliance_bw))
                alliance_name = api.GetUTF8Text()

    if check_page_needed(2):
        # kills tier
        secure_adb_tap(rok_ui.tap_positions["open_kills"], port)
        state_callback("Scanning kills page")
        time.sleep(1 + random_delay())

        secure_adb_screencap(port).save("kills_tier.png")
        image2 = cv2.imread("kills_tier.png")
        image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)

        with PyTessBaseAPI(
            path="./deps/tessdata-main", psm=PSM.SINGLE_WORD, oem=OEM.LSTM_ONLY
        ) as api:
            if scan_options["T1 Kills"]:
                # tier 1 Kills
                im_kills_tier1 = cropToRegion(image2, rok_ui.ocr_regions["t1_kills"])
                im_kills_tier1_bw = preprocessImage(im_kills_tier1, 150, 12)

                api.SetImage(Image.fromarray(im_kills_tier1_bw))
                gov_kills_tier1 = api.GetUTF8Text()
                gov_kills_tier1 = re.sub("[^0-9]", "", gov_kills_tier1)

                # tier 1 KP
                im_kp_tier1 = cropToRegion(image2, rok_ui.ocr_regions["t1_killpoints"])
                im_kp_tier1_bw = preprocessImage(im_kp_tier1, 150, 12)

                api.SetImage(Image.fromarray(im_kp_tier1_bw))
                gov_kp_tier1 = api.GetUTF8Text()
                gov_kp_tier1 = re.sub("[^0-9]", "", gov_kp_tier1)

            if scan_options["T2 Kills"]:
                # tier 2 Kills
                im_kills_tier2 = cropToRegion(image2, rok_ui.ocr_regions["t2_kills"])
                im_kills_tier2_bw = preprocessImage(im_kills_tier2, 150, 12)

                api.SetImage(Image.fromarray(im_kills_tier2_bw))
                gov_kills_tier2 = api.GetUTF8Text()
                gov_kills_tier2 = re.sub("[^0-9]", "", gov_kills_tier2)

                # tier 2 KP
                im_kp_tier2 = cropToRegion(image2, rok_ui.ocr_regions["t2_killpoints"])
                im_kp_tier2_bw = preprocessImage(im_kp_tier2, 150, 12)

                api.SetImage(Image.fromarray(im_kp_tier2_bw))
                gov_kp_tier2 = api.GetUTF8Text()
                gov_kp_tier2 = re.sub("[^0-9]", "", gov_kp_tier2)

            if scan_options["T3 Kills"]:
                # tier 3 Kills
                im_kills_tier3 = cropToRegion(image2, rok_ui.ocr_regions["t3_kills"])
                im_kills_tier3_bw = preprocessImage(im_kills_tier3, 150, 12)

                api.SetImage(Image.fromarray(im_kills_tier3_bw))
                gov_kills_tier3 = api.GetUTF8Text()
                gov_kills_tier3 = re.sub("[^0-9]", "", gov_kills_tier3)

                # tier 3 KP
                im_kp_tier3 = cropToRegion(image2, rok_ui.ocr_regions["t3_killpoints"])
                im_kp_tier3_bw = preprocessImage(im_kp_tier3, 150, 12)

                api.SetImage(Image.fromarray(im_kp_tier3_bw))
                gov_kp_tier3 = api.GetUTF8Text()
                gov_kp_tier3 = re.sub("[^0-9]", "", gov_kp_tier3)

            if scan_options["T4 Kills"]:
                # tier 4
                im_kills_tier4 = cropToRegion(image2, rok_ui.ocr_regions["t4_kills"])
                im_kills_tier4_bw = preprocessImage(im_kills_tier4, 150, 12)

                api.SetImage(Image.fromarray(im_kills_tier4_bw))
                gov_kills_tier4 = api.GetUTF8Text()
                gov_kills_tier4 = re.sub("[^0-9]", "", gov_kills_tier4)

                # tier 4 KP
                im_kp_tier4 = cropToRegion(image2, rok_ui.ocr_regions["t4_killpoints"])
                im_kp_tier4_bw = preprocessImage(im_kp_tier4, 150, 12)

                api.SetImage(Image.fromarray(im_kp_tier4_bw))
                gov_kp_tier4 = api.GetUTF8Text()
                gov_kp_tier4 = re.sub("[^0-9]", "", gov_kp_tier4)

            if scan_options["T5 Kills"]:
                # tier 5
                im_kills_tier5 = cropToRegion(image2, rok_ui.ocr_regions["t5_kills"])
                im_kills_tier5_bw = preprocessImage(im_kills_tier5, 150, 12)

                api.SetImage(Image.fromarray(im_kills_tier5_bw))
                gov_kills_tier5 = api.GetUTF8Text()
                gov_kills_tier5 = re.sub("[^0-9]", "", gov_kills_tier5)

                # tier 5 KP
                im_kp_tier5 = cropToRegion(image2, rok_ui.ocr_regions["t5_killpoints"])
                im_kp_tier5_bw = preprocessImage(im_kp_tier5, 150, 12)

                api.SetImage(Image.fromarray(im_kp_tier5_bw))
                gov_kp_tier5 = api.GetUTF8Text()
                gov_kp_tier5 = re.sub("[^0-9]", "", gov_kp_tier5)

            if scan_options["Ranged"]:
                # ranged points
                im_ranged_points = cropToRegion(
                    image2, rok_ui.ocr_regions["ranged_points"]
                )
                im_ranged_points_bw = preprocessImage(im_ranged_points, 150, 12)

                api.SetImage(Image.fromarray(im_ranged_points_bw))
                gov_ranged_points = api.GetUTF8Text()
                gov_ranged_points = re.sub("[^0-9]", "", gov_ranged_points)

    if check_page_needed(3):
        # More info tab
        secure_adb_tap(rok_ui.tap_positions["more_info"], port)
        state_callback("Scanning more info page")
        time.sleep(1 + random_delay())
        secure_adb_screencap(port).save("more_info.png")
        image3 = cv2.imread("more_info.png")

        with PyTessBaseAPI(
            path="./deps/tessdata-main", psm=PSM.SINGLE_WORD, oem=OEM.LSTM_ONLY
        ) as api:
            if scan_options["Deads"]:
                im_dead = cropToRegion(image3, rok_ui.ocr_regions["deads"])
                im_dead_bw = preprocessImage(im_dead, 150, 12, True)

                api.SetImage(Image.fromarray(im_dead_bw))
                gov_dead = api.GetUTF8Text()
                gov_dead = re.sub("[^0-9]", "", gov_dead)

            if scan_options["Rss Assistance"]:
                im_rss_assistance = cropToRegion(
                    image3, rok_ui.ocr_regions["rss_assisted"]
                )
                im_rss_assistance_bw = preprocessImage(im_rss_assistance, 150, 12, True)

                api.SetImage(Image.fromarray(im_rss_assistance_bw))
                gov_rss_assistance = api.GetUTF8Text()
                gov_rss_assistance = re.sub("[^0-9]", "", gov_rss_assistance)

            if scan_options["Rss Gathered"]:
                im_rss_gathered = cropToRegion(
                    image3, rok_ui.ocr_regions["rss_gathered"]
                )
                im_rss_gathered_bw = preprocessImage(im_rss_gathered, 150, 12, True)

                api.SetImage(Image.fromarray(im_rss_gathered_bw))
                gov_rss_gathered = api.GetUTF8Text()
                gov_rss_gathered = re.sub("[^0-9]", "", gov_rss_gathered)

            if scan_options["Helps"]:
                im_helps = cropToRegion(image3, rok_ui.ocr_regions["alliance_helps"])
                im_helps_bw = preprocessImage(im_helps, 150, 12, True)

                api.SetImage(Image.fromarray(im_helps_bw))
                gov_helps = api.GetUTF8Text()
                gov_helps = re.sub("[^0-9]", "", gov_helps)

    # Just to check the progress, printing in cmd the result for each governor
    if gov_power == "":
        gov_power = "Unknown"
    if gov_killpoints == "":
        gov_killpoints = "Unknown"
    if gov_dead == "":
        gov_dead = "Unknown"
    if gov_kills_tier1 == "":
        gov_kills_tier1 = "Unknown"
    if gov_kills_tier2 == "":
        gov_kills_tier2 = "Unknown"
    if gov_kills_tier3 == "":
        gov_kills_tier3 = "Unknown"
    if gov_kills_tier4 == "":
        gov_kills_tier4 = "Unknown"
    if gov_kills_tier5 == "":
        gov_kills_tier5 = "Unknown"
    if gov_ranged_points == "":
        gov_ranged_points = "Unknown"
    if gov_rss_assistance == "":
        gov_rss_assistance = "Unknown"
    if gov_helps == "":
        gov_helps = "Unknown"

    if scan_options["T4 Kills"] and scan_options["T5 Kills"]:
        gov_kills_tier45 = to_int_check(gov_kills_tier4) + to_int_check(gov_kills_tier5)

        if (
            scan_options["T1 Kills"]
            and scan_options["T2 Kills"]
            and scan_options["T3 Kills"]
        ):
            gov_kills_total = (
                to_int_check(gov_kills_tier1)
                + to_int_check(gov_kills_tier2)
                + to_int_check(gov_kills_tier3)
                + gov_kills_tier45
            )

    state_callback("Closing governor")
    if check_page_needed(3):
        secure_adb_tap(rok_ui.tap_positions["close_info"], port)  # close more info
        time.sleep(0.5 + random_delay())
    secure_adb_tap(rok_ui.tap_positions["close_gov"], port)  # close governor info
    time.sleep(1 + random_delay())

    end_time = time.time()

    print("Time needed for governor: " + str((end_time - start_time)))
    scan_times.append(end_time - start_time)

    return {
        "id": gov_id,
        "name": gov_name,
        "power": gov_power,
        "killpoints": gov_killpoints,
        "kills_t1": gov_kills_tier1,
        "kp_t1": gov_kp_tier1,
        "kills_t2": gov_kills_tier2,
        "kp_t2": gov_kp_tier2,
        "kills_t3": gov_kills_tier3,
        "kp_t3": gov_kp_tier3,
        "kills_t4": gov_kills_tier4,
        "kp_t4": gov_kp_tier4,
        "kills_t5": gov_kills_tier5,
        "kp_t5": gov_kp_tier5,
        "kills_t45": gov_kills_tier45,
        "kills_total": gov_kills_total,
        "ranged_points": gov_ranged_points,
        "dead": gov_dead,
        "rss_assistance": gov_rss_assistance,
        "rss_gathered": gov_rss_gathered,
        "helps": gov_helps,
        "alliance": alliance_name,
        "inactives": inactive_players,
    }


def scan(
    port: int,
    kingdom: str,
    amount: int,
    resume: bool,
    track_inactives: bool,
    validate_kills: bool,
    reconstruct_fails: bool,
    callback=lambda _: (),
    state_callback=lambda _: (),
):
    # Initialize the connection to adb
    start_adb(port)

    if track_inactives:
        Path(f"./inactives/{start_date}/{run_id}").mkdir(parents=True, exist_ok=True)

    review_path = f"./manual_review/{start_date}/{run_id}"

    ######Excel Formatting
    wb = Workbook()
    sheet1 = wb.active
    sheet1.title = str(datetime.date.today())

    # Make Head Bold
    font = Font(bold=True)

    colNames = assign_columns()

    # Initialize Excel Sheet Header
    createHeader("Governor ID", "ID", colNames, sheet1, font)
    createHeader("Governor Name", "Name", colNames, sheet1, font)
    createHeader("Power", "Power", colNames, sheet1, font)
    createHeader("Kill Points", "Killpoints", colNames, sheet1, font)
    createHeader("Deaths", "Deads", colNames, sheet1, font)
    createHeader("T1", "T1 Kills", colNames, sheet1, font)
    createHeader("T2", "T2 Kills", colNames, sheet1, font)
    createHeader("T3", "T3 Kills", colNames, sheet1, font)
    createHeader("T4", "T4 Kills", colNames, sheet1, font)
    createHeader("T5", "T5 Kills", colNames, sheet1, font)
    createHeader("Kills", "Total Kills", colNames, sheet1, font)
    createHeader("Kills (T4+)", "T45 Kills", colNames, sheet1, font)
    createHeader("Ranged Points", "Ranged", colNames, sheet1, font)
    createHeader("RSS Gathered", "Rss Gathered", colNames, sheet1, font)
    createHeader("RSS Assistance", "Rss Assistance", colNames, sheet1, font)
    createHeader("Helps", "Helps", colNames, sheet1, font)
    createHeader("Alliance", "Alliance", colNames, sheet1, font)

    # Counter for fails
    inactive_players = 0

    # Positions for next governor to check
    Y = [285, 390, 490, 590, 605, 705, 805]

    # Resume Scan options. Refine the loop
    j = 0
    if resume:
        j = 4
        amount = amount + j
    # The loop in TOP XXX Governors in kingdom - It works both for power and killpoints Rankings
    # MUST have the tab opened to the 1st governor(Power or Killpoints)

    stop = False
    last_two = False
    next_gov_to_scan = -1

    for i in range(j, amount):
        if scan_abort:
            console.print("Scan Terminated! Saving the current progress...")
            break

        next_gov_to_scan = max(next_gov_to_scan + 1, i)
        governor = governor_scan(
            port, next_gov_to_scan, inactive_players, track_inactives, state_callback
        )
        inactive_players = governor["inactives"]

        if sheet1["A" + str(i + 1 - j)].value == to_int_check(governor["id"]):
            roi = (196, 698, 52, 27)
            secure_adb_screencap(port).save("currentState.png")
            image = cv2.imread("currentState.png")

            im_ranking = cropToRegion(image, roi)
            im_ranking_bw = preprocessImage(im_ranking, 90, 12, True)

            ranking = ""

            with PyTessBaseAPI(
                path="./deps/tessdata-main", psm=PSM.SINGLE_WORD, oem=OEM.LSTM_ONLY
            ) as api:
                api.SetImage(Image.fromarray(im_ranking_bw))
                ranking = api.GetUTF8Text()
                ranking = re.sub("[^0-9]", "", ranking)

            if ranking == "" or to_int_check(ranking) != 999:
                console.log(
                    f"Duplicate governor detected, but current rank is {ranking}, trying a second time."
                )
                logging.log(
                    logging.INFO,
                    f"Duplicate governor detected, but current rank is {ranking}, trying a second time.",
                )

                # repeat scan with next governor
                governor = governor_scan(
                    port, next_gov_to_scan, inactive_players, track_inactives
                )
                inactive_players = governor["inactives"]
            else:
                if not last_two:
                    last_two = True
                    next_gov_to_scan = 998
                    console.log(
                        "Duplicate governor detected, switching to scanning of last two governors."
                    )
                    logging.log(
                        logging.INFO,
                        "Duplicate governor detected, switching to scanning of last two governors.",
                    )

                    # repeat scan with next governor
                    governor = governor_scan(
                        port, next_gov_to_scan, inactive_players, track_inactives
                    )
                    inactive_players = governor["inactives"]
                else:
                    console.log("Reached final governor on the screen. Scan complete.")
                    logging.log(
                        logging.INFO,
                        "Reached final governor on the screen. Scan complete.",
                    )
                    state_callback("Scan finished")
                    exit(0)

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")

        kills_ok = "Not Checked"
        if validate_kills:
            kills_ok = are_kills_ok(
                to_int_check(governor["kills_t1"]),
                to_int_check(governor["kills_t2"]),
                to_int_check(governor["kills_t3"]),
                to_int_check(governor["kills_t4"]),
                to_int_check(governor["kills_t5"]),
                to_int_check(governor["killpoints"]),
            )
        kp_ok = False

        if not kills_ok:
            Path(review_path).mkdir(parents=True, exist_ok=True)
            kp_ok = are_kp_ok(
                to_int_check(governor["kp_t1"]),
                to_int_check(governor["kp_t2"]),
                to_int_check(governor["kp_t3"]),
                to_int_check(governor["kp_t4"]),
                to_int_check(governor["kp_t5"]),
                to_int_check(governor["killpoints"]),
            )

            if not reconstruct_fails or not kp_ok:
                shutil.copy(
                    Path("./gov_info.png"),
                    Path(f"""{review_path}/F{governor["id"]}-profile.png"""),
                )
                shutil.copy(
                    Path("./kills_tier.png"),
                    Path(f"""{review_path}/F{governor["id"]}-kills.png"""),
                )
                logging.log(
                    logging.WARNING,
                    f"""Kills for {governor["name"]} ({to_int_check(governor["id"])}) don't check out, manually need to look at them!""",
                )
            else:
                kills_t1, kills_t2, kills_t3, kills_t4, kills_t5 = calculate_kills(
                    to_int_check(governor["kills_t1"]),
                    to_int_check(governor["kp_t1"]),
                    to_int_check(governor["kp_t2"]),
                    to_int_check(governor["kp_t3"]),
                    to_int_check(governor["kp_t4"]),
                    to_int_check(governor["kp_t5"]),
                )
                governor["kills_t1"] = kills_t1
                governor["kills_t2"] = kills_t2
                governor["kills_t3"] = kills_t3
                governor["kills_t4"] = kills_t4
                governor["kills_t5"] = kills_t5

                shutil.copy(
                    Path("./gov_info.png"),
                    Path(
                        f"""{review_path}/R{governor["id"]}-profile-reconstructed.png"""
                    ),
                )
                shutil.copy(
                    Path("./kills_tier.png"),
                    Path(
                        f"""{review_path}/R{governor["id"]}-kills-reconstructed.png"""
                    ),
                )
                logging.log(
                    logging.INFO,
                    f"""Kills for {governor["name"]} ({to_int_check(governor["id"])}) reconstructed, t1 might be off by up to 4 kills.""",
                )

        # nice output for console
        table = Table(
            title="["
            + current_time
            + "]\n"
            + "Latest Scan Result\nGovernor "
            + str(i + 1)
            + " of "
            + str(amount),
            show_header=True,
            show_footer=True,
        )

        if not reconstruct_fails or kills_ok:
            table.add_column(
                "Entry",
                "Approx time remaining\nSkipped\nKills check out",
                style="magenta",
            )
            table.add_column(
                "Value",
                str(datetime.timedelta(seconds=get_remaining_time(amount - i)))
                + "\n"
                + str(inactive_players)
                + "\n"
                + str(kills_ok),
                style="cyan",
            )
        else:
            table.add_column(
                "Entry",
                "Approx time remaining\nSkipped\nKills check out\nReconstruct success",
                style="magenta",
            )
            table.add_column(
                "Value",
                str(datetime.timedelta(seconds=get_remaining_time(amount - i)))
                + "\n"
                + str(inactive_players)
                + "\n"
                + str(kills_ok)
                + "\n"
                + str(kp_ok),
                style="cyan",
            )

        table.add_row("Governor ID", str(governor["id"]))
        table.add_row("Governor Name", governor["name"])
        table.add_row("Governor Power", str(governor["power"]))
        table.add_row("Governor Kill Points", str(governor["killpoints"]))
        table.add_row("Governor Deads", str(governor["dead"]))
        table.add_row("Governor T1 Kills", str(governor["kills_t1"]).rstrip())
        table.add_row("Governor T2 Kills", str(governor["kills_t2"]).rstrip())
        table.add_row("Governor T3 Kills", str(governor["kills_t3"]).rstrip())
        table.add_row("Governor T4 Kills", str(governor["kills_t4"]).rstrip())
        table.add_row("Governor T5 Kills", str(governor["kills_t5"]).rstrip())
        table.add_row("Governor T4+5 Kills", str(governor["kills_t45"]))
        table.add_row("Governor Total Kills", str(governor["kills_total"]))
        table.add_row("Governor Ranged Points", str(governor["ranged_points"]).rstrip())
        table.add_row("Governor RSS Assistance", str(governor["rss_assistance"]))
        table.add_row("Governor RSS Gathered", str(governor["rss_gathered"]))
        table.add_row("Governor Helps", str(governor["helps"]))
        table.add_row("Governor Alliance", escape(governor["alliance"].rstrip()))

        console.print(table)

        # fmt: off
        # Write results in excel file
        current_row = i + 2 - j
        setCell(sheet1, colNames, "ID", current_row, to_int_check(governor["id"]))
        setCell(sheet1, colNames, "Name", current_row, governor["name"])
        setCell(sheet1, colNames, "Power", current_row, to_int_check(governor["power"]))
        setCell(sheet1, colNames, "Killpoints", current_row, to_int_check(governor["killpoints"]))
        setCell(sheet1, colNames, "Deads", current_row, to_int_check(governor["dead"]))
        setCell(sheet1, colNames, "T1 Kills", current_row, to_int_check(governor["kills_t1"]))
        setCell(sheet1, colNames, "T2 Kills", current_row, to_int_check(governor["kills_t2"]))
        setCell(sheet1, colNames, "T3 Kills", current_row, to_int_check(governor["kills_t3"]))
        setCell(sheet1, colNames, "T4 Kills", current_row, to_int_check(governor["kills_t4"]))
        setCell(sheet1, colNames, "T5 Kills", current_row, to_int_check(governor["kills_t5"]))
        setCell(sheet1, colNames, "Total Kills", current_row, to_int_check(governor["kills_total"]))
        setCell(sheet1, colNames, "T45 Kills", current_row, to_int_check(governor["kills_t45"]))
        setCell(sheet1, colNames, "Ranged", current_row, to_int_check(governor["ranged_points"]))
        setCell(sheet1, colNames, "Rss Gathered", current_row, to_int_check(governor["rss_gathered"]))
        setCell(sheet1, colNames, "Rss Assistance", current_row, to_int_check(governor["rss_assistance"]))
        setCell(sheet1, colNames, "Helps", current_row, to_int_check(governor["helps"]))
        setCell(sheet1, colNames, "Alliance", current_row, governor["alliance"].rstrip())
        # fmt: on

        if resume:
            file_name_prefix = "NEXT"
        else:
            file_name_prefix = "TOP"
        wb.save(
            file_name_prefix
            + str(amount - j)
            + "-"
            + str(datetime.date.today())
            + "-"
            + kingdom
            + f"-[{run_id}]"
            + ".xlsx"
        )

        additional_info = {
            "govs": f"{i + 1} of {amount}",
            "skipped": f"Skipped {inactive_players}",
            "time": current_time,
            "eta": format_timedelta_to_HHMMSS(
                datetime.timedelta(seconds=get_remaining_time(amount - i))
            ),
        }
        governor.update(additional_info)
        callback(governor)

    if resume:
        file_name_prefix = "NEXT"
    else:
        file_name_prefix = "TOP"
    wb.save(
        file_name_prefix
        + str(amount - j)
        + "-"
        + str(datetime.date.today())
        + "-"
        + kingdom
        + f"-[{run_id}]"
        + ".xlsx"
    )
    console.log("Reached the target amount of people. Scan complete.")
    logging.log(logging.INFO, "Reached the target amount of people. Scan complete.")
    kill_adb()  # make sure to clean up adb server
    state_callback("Scan finished")
    return


def end_scan():
    global scan_abort
    scan_abort = True


def start_from_gui(general_options, scan_options_new, callback, state_callback):
    global run_id
    global start_date
    global new_scroll
    global scan_options
    global scan_abort
    global scan_times

    scan_times = []
    scan_abort = False
    run_id = general_options["uuid"]
    start_date = datetime.date.today()
    scan_options = scan_options_new

    scan(
        general_options["port"],
        general_options["name"],
        general_options["amount"],
        general_options["resume"],
        general_options["inactives"],
        general_options["validate"],
        general_options["reconstruct"],
        callback,
        state_callback,
    )


def main():
    signal.signal(signal.SIGINT, stopHandler)
    console.print(
        "Tesseract languages available: "
        + str(tesserocr.get_languages("./deps/tessdata-main"))
    )
    global run_id
    global start_date
    global new_scroll
    global scan_options
    bluestacks_device_name = "RoK Tracker"
    run_id = generate_random_id(8)
    start_date = datetime.date.today()
    console.print(f"The UUID of this scan is [green]{run_id}[/green]", highlight=False)

    bluestacks_device_name = questionary.text(
        message="Name of your bluestacks instance:", default=bluestacks_device_name
    ).ask()

    bluestacks_port = int(
        questionary.text(
            f"Adb port of device (detected {get_bluestacks_port(bluestacks_device_name)}):",
            default=str(get_bluestacks_port(bluestacks_device_name)),
            validate=lambda port: is_string_int(port),
        ).ask()
    )

    kingdom = questionary.text(message="Kingdom name (used for file name):").ask()

    scan_amount = int(
        questionary.text(
            message="Number of people to scan:",
            validate=lambda port: is_string_int(port),
        ).ask()
    )

    resume_scan = questionary.confirm(
        message="Resume scan:", auto_enter=False, default=False
    ).ask()

    new_scroll = questionary.confirm(
        message="Use advanced scrolling method:", auto_enter=False, default=True
    ).ask()

    track_inactives = questionary.confirm(
        message="Screenshot inactives:", auto_enter=False, default=False
    ).ask()

    scan_mode = questionary.select(
        "What scan do you want to do?",
        choices=[
            questionary.Choice(
                "Full (Everything the scanner can)",
                value="full",
                checked=True,
                shortcut_key="f",
            ),
            questionary.Choice(
                "Seed (ID, Name, Power, KP, Alliance)",
                value="seed",
                checked=False,
                shortcut_key="s",
            ),
            questionary.Choice(
                "Custom (select needed items in next step)",
                value="custom",
                checked=False,
                shortcut_key="c",
            ),
        ],
    ).ask()

    match scan_mode:
        case "full":
            scan_options = {
                "ID": True,
                "Name": True,
                "Power": True,
                "Killpoints": True,
                "Alliance": True,
                "T1 Kills": True,
                "T2 Kills": True,
                "T3 Kills": True,
                "T4 Kills": True,
                "T5 Kills": True,
                "Ranged": True,
                "Deads": True,
                "Rss Assistance": True,
                "Rss Gathered": True,
                "Helps": True,
            }
        case "seed":
            scan_options = {
                "ID": True,
                "Name": True,
                "Power": True,
                "Killpoints": True,
                "Alliance": True,
                "T1 Kills": False,
                "T2 Kills": False,
                "T3 Kills": False,
                "T4 Kills": False,
                "T5 Kills": False,
                "Ranged": False,
                "Deads": False,
                "Rss Assistance": False,
                "Rss Gathered": False,
                "Helps": False,
            }
        case "custom":
            items_to_scan = questionary.checkbox(
                "What stats should be scanned?",
                choices=[
                    questionary.Choice(
                        "ID",
                        checked=False,
                    ),
                    questionary.Choice(
                        "Name",
                        checked=False,
                    ),
                    questionary.Choice(
                        "Power",
                        checked=False,
                    ),
                    questionary.Choice(
                        "Killpoints",
                        checked=False,
                    ),
                    questionary.Choice(
                        "Alliance",
                        checked=False,
                    ),
                    questionary.Choice(
                        "T1 Kills",
                        checked=False,
                    ),
                    questionary.Choice(
                        "T2 Kills",
                        checked=False,
                    ),
                    questionary.Choice(
                        "T3 Kills",
                        checked=False,
                    ),
                    questionary.Choice(
                        "T4 Kills",
                        checked=False,
                    ),
                    questionary.Choice(
                        "T5 Kills",
                        checked=False,
                    ),
                    questionary.Choice(
                        "Ranged",
                        checked=False,
                    ),
                    questionary.Choice(
                        "Deads",
                        checked=False,
                    ),
                    questionary.Choice(
                        "Rss Assistance",
                        checked=False,
                    ),
                    questionary.Choice(
                        "Rss Gathered",
                        checked=False,
                    ),
                    questionary.Choice(
                        "Helps",
                        checked=False,
                    ),
                ],
            ).ask()
            if items_to_scan == [] or items_to_scan == None:
                console.print("Exiting, no items selected.")
                exit(0)
            else:
                for item in items_to_scan:
                    scan_options[item] = True
        case _:
            console.print("Exiting, no mode selected.")
            exit(0)

    validate_kills = False
    reconstruct_fails = False

    if (
        scan_options["T1 Kills"]
        and scan_options["T2 Kills"]
        and scan_options["T3 Kills"]
        and scan_options["T4 Kills"]
        and scan_options["T5 Kills"]
        and scan_options["Killpoints"]
    ):
        validate_kills = questionary.confirm(
            message="Validate killpoints:",
            auto_enter=False,
            default=True,
        ).ask()

    if validate_kills:
        reconstruct_fails = questionary.confirm(
            message="Try reconstructiong wrong kills values:",
            auto_enter=False,
            default=True,
        ).ask()

    scan(
        bluestacks_port,
        kingdom,
        scan_amount,
        resume_scan,
        track_inactives,
        validate_kills,
        reconstruct_fails,
    )
    exit(1)


if __name__ == "__main__":
    main()
