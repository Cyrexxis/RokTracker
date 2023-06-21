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
from rich.prompt import Prompt
from rich.prompt import IntPrompt
from rich.prompt import Confirm
from rich.table import Table
from rich.markup import escape
from openpyxl import Workbook
from openpyxl.styles import Font
from pathlib import Path
from adbutils import *
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
bluestacks_device_name = "RoK Tracker"
scan_times = []


def random_delay() -> float:
    return random.random() * 0.1


def get_remaining_time(remaining_govs: int) -> float:
    return (sum(scan_times, start=0) / len(scan_times)) * remaining_govs


def get_bluestacks_port():
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
    stop = Confirm.ask("Do you really want to exit?")
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


def governor_scan(
    port: int, current_player: int, inactive_players: int, track_inactives: bool
):
    start_time = time.time()
    # set up the scan variables
    gov_name = ""
    gov_id = 0
    gov_power = 0
    gov_killpoints = 0
    gov_dead = 0
    gov_kills_tier1 = 0
    gov_kills_tier2 = 0
    gov_kills_tier3 = 0
    gov_kills_tier4 = 0
    gov_kills_tier5 = 0
    gov_ranged_points = 0
    gov_rss_assistance = 0
    gov_helps = 0
    alliance_name = ""

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
        roi = (313, 727, 137, 29)  # Checking for more info
        im_check_more_info = cropToRegion(image_check, roi)
        # check_more_info = pytesseract.image_to_string(im_check_more_info,config="-c tessedit_char_whitelist=MoreInfo")
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
                cont = Confirm.ask("Could not find user, retry?", default=True)
                if cont:
                    count = 0
                else:
                    break
        else:
            gov_info = True
            break

    # nickname copy

    copy_try = 0
    while copy_try < 3:
        try:
            secure_adb_shell(f"input tap 690 283", port)
            time.sleep(0.2)
            gov_name = tk.Tk().clipboard_get()
            break
        except:
            console.log("Name copy failed, retying")
            logging.log(logging.INFO, "Name copy failed, retying")
            copy_try = copy_try + 1

    time.sleep(1.5 + random_delay())

    secure_adb_screencap(port).save("gov_info.png")
    image = cv2.imread("gov_info.png")

    # Power and Killpoints
    roi = (774, 230, 260, 38)
    im_gov_id = cropToRegion(image, roi)
    im_gov_id_gray = cv2.cvtColor(im_gov_id, cv2.COLOR_BGR2GRAY)
    im_gov_id_gray = cv2.bitwise_not(im_gov_id_gray)
    (thresh, im_gov_id_bw) = cv2.threshold(im_gov_id_gray, 120, 255, cv2.THRESH_BINARY)

    roi = (890, 364, 170, 44)
    im_gov_power = cropToRegion(image, roi)
    im_gov_power_bw = preprocessImage(im_gov_power, 100, 12, True)

    roi = (1114, 364, 222, 44)
    im_gov_killpoints = cropToRegion(image, roi)
    im_gov_killpoints_bw = preprocessImage(im_gov_killpoints, 100, 12, True)

    roi = (645, 362, 260, 40)  # alliance tag
    im_alliance_tag = cropToRegion(image, roi)

    # kills tier
    secure_adb_shell(f"input tap 1118 350", port)

    # 1st image data
    with PyTessBaseAPI(
        path="./deps/tessdata-main", psm=PSM.SINGLE_WORD, oem=OEM.LSTM_ONLY
    ) as api:
        api.SetImage(Image.fromarray(im_gov_power_bw))
        gov_power = api.GetUTF8Text()
        gov_power = re.sub("[^0-9]", "", gov_power)

        api.SetImage(Image.fromarray(im_gov_killpoints_bw))
        gov_killpoints = api.GetUTF8Text()
        gov_killpoints = re.sub("[^0-9]", "", gov_killpoints)

        api.SetPageSegMode(PSM.SINGLE_LINE)
        api.SetImage(Image.fromarray(im_gov_id_bw))
        gov_id = api.GetUTF8Text()
        gov_id = re.sub("[^0-9]", "", gov_id)

    # gov_id = pytesseract.image_to_string(im_gov_id_bw,config="--psm 7")
    # gov_id = int(re.sub("[^0-9]", "", gov_id))

    # gov_power = pytesseract.image_to_string(im_gov_power_bw,config="--oem 1 --psm 8")
    # gov_power = int(re.sub("[^0-9]", "", gov_power))

    # gov_killpoints = pytesseract.image_to_string(im_gov_killpoints_bw,config="--oem 1 --psm 8")
    # gov_killpoints = int(re.sub("[^0-9]", "", gov_killpoints))

    time.sleep(1 + random_delay())

    secure_adb_screencap(port).save("kills_tier.png")
    image2 = cv2.imread("kills_tier.png")
    image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)

    roi = (862, 461, 150, 38)  # tier 1
    im_kills_tier1 = cropToRegion(image2, roi)
    im_kills_tier1_bw = preprocessImage(im_kills_tier1, 150, 12)

    roi = (1243, 461, 171, 38)  # tier 1 KP
    im_kp_tier1 = cropToRegion(image2, roi)
    im_kp_tier1_bw = preprocessImage(im_kp_tier1, 150, 12)

    roi = (862, 505, 150, 38)  # tier 2
    im_kills_tier2 = cropToRegion(image2, roi)
    im_kills_tier2_bw = preprocessImage(im_kills_tier2, 150, 12)

    roi = (1243, 505, 171, 38)  # tier 2 KP
    im_kp_tier2 = cropToRegion(image2, roi)
    im_kp_tier2_bw = preprocessImage(im_kp_tier2, 150, 12)

    roi = (862, 549, 150, 38)  # tier 3
    im_kills_tier3 = cropToRegion(image2, roi)
    im_kills_tier3_bw = preprocessImage(im_kills_tier3, 150, 12)

    roi = (1243, 549, 171, 38)  # tier 3 KP
    im_kp_tier3 = cropToRegion(image2, roi)
    im_kp_tier3_bw = preprocessImage(im_kp_tier3, 150, 12)

    roi = (862, 593, 150, 38)  # tier 4
    im_kills_tier4 = cropToRegion(image2, roi)
    im_kills_tier4_bw = preprocessImage(im_kills_tier4, 150, 12)

    roi = (1243, 593, 171, 38)  # tier 4 KP
    im_kp_tier4 = cropToRegion(image2, roi)
    im_kp_tier4_bw = preprocessImage(im_kp_tier4, 150, 12)

    roi = (862, 638, 150, 38)  # tier 5
    im_kills_tier5 = cropToRegion(image2, roi)
    im_kills_tier5_bw = preprocessImage(im_kills_tier5, 150, 12)

    roi = (1243, 638, 171, 38)  # tier 5 KP
    im_kp_tier5 = cropToRegion(image2, roi)
    im_kp_tier5_bw = preprocessImage(im_kp_tier5, 150, 12)

    roi = (1274, 740, 146, 38)  # ranged points
    im_ranged_points = cropToRegion(image2, roi)
    im_ranged_points_bw = preprocessImage(im_ranged_points, 150, 12)

    # More info tab
    secure_adb_shell(f"input tap 387 664", port)

    with PyTessBaseAPI(
        path="./deps/tessdata-main", psm=PSM.SINGLE_WORD, oem=OEM.LSTM_ONLY
    ) as api:
        api.SetImage(Image.fromarray(im_kills_tier1_bw))
        gov_kills_tier1 = api.GetUTF8Text()
        gov_kills_tier1 = re.sub("[^0-9]", "", gov_kills_tier1)

        api.SetImage(Image.fromarray(im_kp_tier1_bw))
        gov_kp_tier1 = api.GetUTF8Text()
        gov_kp_tier1 = re.sub("[^0-9]", "", gov_kp_tier1)

        api.SetImage(Image.fromarray(im_kills_tier2_bw))
        gov_kills_tier2 = api.GetUTF8Text()
        gov_kills_tier2 = re.sub("[^0-9]", "", gov_kills_tier2)

        api.SetImage(Image.fromarray(im_kp_tier2_bw))
        gov_kp_tier2 = api.GetUTF8Text()
        gov_kp_tier2 = re.sub("[^0-9]", "", gov_kp_tier2)

        api.SetImage(Image.fromarray(im_kills_tier3_bw))
        gov_kills_tier3 = api.GetUTF8Text()
        gov_kills_tier3 = re.sub("[^0-9]", "", gov_kills_tier3)

        api.SetImage(Image.fromarray(im_kp_tier3_bw))
        gov_kp_tier3 = api.GetUTF8Text()
        gov_kp_tier3 = re.sub("[^0-9]", "", gov_kp_tier3)

        api.SetImage(Image.fromarray(im_kills_tier4_bw))
        gov_kills_tier4 = api.GetUTF8Text()
        gov_kills_tier4 = re.sub("[^0-9]", "", gov_kills_tier4)

        api.SetImage(Image.fromarray(im_kp_tier4_bw))
        gov_kp_tier4 = api.GetUTF8Text()
        gov_kp_tier4 = re.sub("[^0-9]", "", gov_kp_tier4)

        api.SetImage(Image.fromarray(im_kills_tier5_bw))
        gov_kills_tier5 = api.GetUTF8Text()
        gov_kills_tier5 = re.sub("[^0-9]", "", gov_kills_tier5)

        api.SetImage(Image.fromarray(im_kp_tier5_bw))
        gov_kp_tier5 = api.GetUTF8Text()
        gov_kp_tier5 = re.sub("[^0-9]", "", gov_kp_tier5)

        api.SetImage(Image.fromarray(im_ranged_points_bw))
        gov_ranged_points = api.GetUTF8Text()
        gov_ranged_points = re.sub("[^0-9]", "", gov_ranged_points)

    time.sleep(1 + random_delay())
    secure_adb_screencap(port).save("more_info.png")
    image3 = cv2.imread("more_info.png")

    roi = (1130, 443, 183, 40)  # dead
    im_dead = cropToRegion(image3, roi)
    im_dead_bw = preprocessImage(im_dead, 150, 12, True)

    roi = (1130, 668, 183, 40)  # rss assistance
    im_rss_assistance = cropToRegion(image3, roi)
    im_rss_assistance_bw = preprocessImage(im_rss_assistance, 150, 12, True)

    roi = (1130, 735, 183, 40)  # alliance helps
    im_helps = cropToRegion(image3, roi)
    im_helps_bw = preprocessImage(im_helps, 150, 12, True)

    roi = (1130, 612, 183, 40)  # rss gathered
    im_rss_gathered = cropToRegion(image3, roi)
    im_rss_gathered_bw = preprocessImage(im_rss_gathered, 150, 12, True)

    with PyTessBaseAPI(
        path="./deps/tessdata-main", psm=PSM.SINGLE_WORD, oem=OEM.LSTM_ONLY
    ) as api:
        api.SetImage(Image.fromarray(im_dead_bw))
        gov_dead = api.GetUTF8Text()
        gov_dead = re.sub("[^0-9]", "", gov_dead)

        api.SetImage(Image.fromarray(im_rss_gathered_bw))
        gov_rss_gathered = api.GetUTF8Text()
        gov_rss_gathered = re.sub("[^0-9]", "", gov_rss_gathered)

        api.SetImage(Image.fromarray(im_rss_assistance_bw))
        gov_rss_assistance = api.GetUTF8Text()
        gov_rss_assistance = re.sub("[^0-9]", "", gov_rss_assistance)

        api.SetImage(Image.fromarray(im_helps_bw))
        gov_helps = api.GetUTF8Text()
        gov_helps = re.sub("[^0-9]", "", gov_helps)

        api.SetPageSegMode(PSM.SINGLE_LINE)
        im_alliance_bw = preprocessImage(im_alliance_tag, 50, 12, True)
        api.SetImage(Image.fromarray(im_alliance_bw))
        alliance_name = api.GetUTF8Text()

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

    gov_kills_tier45 = to_int_check(gov_kills_tier4) + to_int_check(gov_kills_tier5)
    gov_kills_total = (
        to_int_check(gov_kills_tier1)
        + to_int_check(gov_kills_tier2)
        + to_int_check(gov_kills_tier3)
        + gov_kills_tier45
    )

    secure_adb_shell(f"input tap 1396 58", port)  # close more info
    time.sleep(0.5 + random_delay())
    secure_adb_shell(f"input tap 1365 104", port)  # close governor info
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
    reconstruct_fails: bool,
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

    # Initialize Excel Sheet Header
    sheet1["A1"] = "Governor ID"
    sheet1["B1"] = "Governor Name"
    sheet1["C1"] = "Power"
    sheet1["D1"] = "Kill Points"
    sheet1["E1"] = "Deaths"
    sheet1["F1"] = "T1"
    sheet1["G1"] = "T2"
    sheet1["H1"] = "T3"
    sheet1["I1"] = "T4"
    sheet1["J1"] = "T5"
    sheet1["K1"] = "Kills"
    sheet1["L1"] = "Kills (T4+)"
    sheet1["M1"] = "Resource Assistance"
    sheet1["N1"] = "Helps"
    sheet1["O1"] = "Alliance"
    sheet1["P1"] = "Ranged Points"
    sheet1["Q1"] = "RSS Gathered"

    sheet1["A1"].font = font
    sheet1["B1"].font = font
    sheet1["C1"].font = font
    sheet1["D1"].font = font
    sheet1["E1"].font = font
    sheet1["F1"].font = font
    sheet1["G1"].font = font
    sheet1["H1"].font = font
    sheet1["I1"].font = font
    sheet1["J1"].font = font
    sheet1["K1"].font = font
    sheet1["L1"].font = font
    sheet1["M1"].font = font
    sheet1["N1"].font = font
    sheet1["O1"].font = font
    sheet1["P1"].font = font
    sheet1["Q1"].font = font

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
            port, next_gov_to_scan, inactive_players, track_inactives
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
                    exit(0)

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")

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
                str(datetime.timedelta(seconds=(amount - i) * 19))
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

        # Write results in excel file
        sheet1["A" + str(i + 2 - j)] = to_int_check(governor["id"])
        sheet1["B" + str(i + 2 - j)] = governor["name"]
        sheet1["C" + str(i + 2 - j)] = to_int_check(governor["power"])
        sheet1["D" + str(i + 2 - j)] = to_int_check(governor["killpoints"])
        sheet1["E" + str(i + 2 - j)] = to_int_check(governor["dead"])
        sheet1["F" + str(i + 2 - j)] = to_int_check(governor["kills_t1"])
        sheet1["G" + str(i + 2 - j)] = to_int_check(governor["kills_t2"])
        sheet1["H" + str(i + 2 - j)] = to_int_check(governor["kills_t3"])
        sheet1["I" + str(i + 2 - j)] = to_int_check(governor["kills_t4"])
        sheet1["J" + str(i + 2 - j)] = to_int_check(governor["kills_t5"])
        sheet1["K" + str(i + 2 - j)] = to_int_check(governor["kills_total"])
        sheet1["L" + str(i + 2 - j)] = to_int_check(governor["kills_t45"])
        sheet1["M" + str(i + 2 - j)] = to_int_check(governor["rss_assistance"])
        sheet1["N" + str(i + 2 - j)] = to_int_check(governor["helps"])
        sheet1["O" + str(i + 2 - j)] = governor["alliance"].rstrip()
        sheet1["P" + str(i + 2 - j)] = to_int_check(governor["ranged_points"])
        sheet1["Q" + str(i + 2 - j)] = to_int_check(governor["rss_gathered"])

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
    return


def main():
    signal.signal(signal.SIGINT, stopHandler)
    console.print(
        "Tesseract languages available: "
        + str(tesserocr.get_languages("./deps/tessdata-main"))
    )
    global run_id
    global start_date
    global new_scroll
    global bluestacks_device_name
    run_id = generate_random_id(8)
    start_date = datetime.date.today()
    console.print(f"The UUID of this scan is [green]{run_id}[/green]", highlight=False)

    bluestacks_device_name = Prompt.ask(
        "Name of your bluestacks instance", default=bluestacks_device_name
    )
    bluestacks_port = IntPrompt.ask("Adb port of device", default=get_bluestacks_port())
    kingdom = Prompt.ask("Kingdom name (used for file name)", default="KD")
    scan_amount = IntPrompt.ask("People to scan", default=600)
    resume_scan = Confirm.ask("Resume scan", default=False)
    new_scroll = Confirm.ask(
        "Use the new scrolling method (more accurate, but might not work)", default=True
    )
    track_inactives = Confirm.ask("Track inactives (via screenshot)", default=False)
    reconstruct_fails = Confirm.ask(
        "Try to reconstruct kills via killpoints", default=True
    )

    scan(
        bluestacks_port,
        kingdom,
        scan_amount,
        resume_scan,
        track_inactives,
        reconstruct_fails,
    )
    exit(1)


if __name__ == "__main__":
    main()
