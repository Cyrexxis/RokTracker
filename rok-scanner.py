from rich.prompt import Prompt
from rich.prompt import IntPrompt
from rich.prompt import Confirm
from rich.console import Console
from rich.table import Table
from ppadb.client import Client
from openpyxl import Workbook
from openpyxl.styles import Font
from PIL import Image
from neural_network import read_ocr
import tkinter as tk
import configparser
import subprocess
import datetime
import time
import random
import cv2
import pytesseract
import signal
import re
import logging
import math

console = Console()
logging.basicConfig(filename='rok-scanner.log', encoding='utf-8', level=logging.DEBUG)

def get_bluestacks_port():
    # try to read port from bluestacks config
    try:
        dummy = "AmazingDummy"
        with open("S:\\Other\\BlueStacks\\BlueStacks_nxt\\bluestacks.conf") as config_file:
            file_content = '[' + dummy + ']\n' + config_file.read()
        config = configparser.RawConfigParser()
        config.read_string(file_content)

        for key, value in config.items(dummy):
            if value == '"RoK Tracker"':
                key_port = key.replace("display_name", "status.adb_port")
                port = config.get(dummy, key_port)
                return int(port.strip('\"'))
    except:
        console.print("[red]Could not parse or find bluestacks config. Defaulting to 5555.[/red]")
        return 5555
    return 5555

def start_adb(port: int):
	console.print("Killing ADB server...")
	process = subprocess.run(['.\\platform-tools\\adb.exe', 'kill-server'], 
                         stdout=subprocess.PIPE, 
                         universal_newlines=True)
	console.print(process.stdout)
	console.print("Starting adb server and connecting to adb device...")
	process = subprocess.run(['.\\platform-tools\\adb.exe', 'connect',  'localhost:' + str(port)], 
                         stdout=subprocess.PIPE, 
                         universal_newlines=True)
	console.print(process.stdout)
	adb = Client(host='localhost', port=5037)
	devices = adb.devices()

	if len(devices) == 0:
		console.print('no device attached')
		quit()

	#Probably a good idea to have only 1 device while running this
	return devices[0]

def secure_adb_shell(command_to_execute: str, device, port: int):
    for i in range(3):
        try:
            device.shell(command_to_execute)
        except:
            console.print("[red]ADB crashed[/red]")
            device = start_adb(port)
        else:
            return

def secure_adb_screencap(device, port: int):
    result = None
    for i in range(3):
        try:
            result = device.screencap()
        except:
            console.print("[red]ADB crashed[/red]")
            device = start_adb(port)
        else:
            return result
    return result

def to_int_check(element):
	try:
		return int(element)
	except ValueError:
		#return element
		return int(0)

def stopHandler(signum, frame):
    stop = Confirm.ask("Do you really want to exit?")
    if stop:
        console.print("Scan aborted.")
        exit(1)

def cropToRegion(image, roi):
     return image[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

def governor_scan(device, port: int, tap_position: int, inactive_players: int, track_inactives: bool):
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

    #Open governor
    secure_adb_shell(f'input tap 690 ' + str(tap_position), device, port)
    time.sleep(2 + random.random())

    gov_info = False
    count = 0

    while not (gov_info):
        image_check_original = secure_adb_screencap(device, port)
        with open(('check_more_info.png'), 'wb') as f:
                    f.write(image_check_original)  # type: ignore
        
        image_check = cv2.imread('check_more_info.png',cv2.IMREAD_GRAYSCALE)
        roi = (313, 727, 137, 29)	#Checking for more info
        im_check_more_info = cropToRegion(image_check, roi)
        check_more_info = pytesseract.image_to_string(im_check_more_info,config="-c tessedit_char_whitelist=MoreInfo")

        # Probably tapped governor is inactive and needs to be skipped
        if 'MoreInfo' not in check_more_info :
            inactive_players += 1
            if track_inactives:
                image_check_inactive = cv2.imread('check_more_info.png')
                roiInactive = (0, tap_position - 100, 1400, 200)
                image_inactive_raw = cropToRegion(image_check_inactive, roiInactive)
                cv2.imwrite(f'Inactive {inactive_players:03}.png', image_inactive_raw)
            secure_adb_shell(f'input swipe 690 605 690 540', device, port)
            secure_adb_shell(f'input tap 690 ' + str(tap_position), device, port)
            count += 1
            time.sleep(2 + random.random())
            if count == 10:
                cont = Confirm.ask("Could not find user, retry?", default=True)
                if(cont):
                    count = 0
                else:
                    break
        else:
            gov_info = True
            break
        
    #nickname copy
    secure_adb_shell(f'input tap 690 283', device, port)
    time.sleep(0.2)
    gov_name = tk.Tk().clipboard_get()
    time.sleep(2 + random.random())

    image = secure_adb_screencap(device, port)
    with open(('gov_info.png'), 'wb') as f:
                f.write(image)  # type: ignore
    image = cv2.imread('gov_info.png')

    #Power and Killpoints
    roi = (642, 230, 260, 38)
    im_gov_id = cropToRegion(image, roi)
    im_gov_id_gray = cv2.cvtColor(im_gov_id, cv2.COLOR_BGR2GRAY)
    im_gov_id_gray = cv2.bitwise_not(im_gov_id_gray)
    (thresh, im_gov_id_bw) = cv2.threshold(im_gov_id_gray, 120, 255, cv2.THRESH_BINARY)

    image = cv2.imread('gov_info.png')
    roi = (890, 364, 170, 44)
    im_gov_power = cropToRegion(image, roi)
    im_gov_power_gray = cv2.cvtColor(im_gov_power, cv2.COLOR_BGR2GRAY)
    im_gov_power_gray = cv2.bitwise_not(im_gov_power_gray)
    (thresh, im_gov_power_bw) = cv2.threshold(im_gov_power_gray, 100, 255, cv2.THRESH_BINARY)

    roi = (1114, 364, 222, 44)
    im_gov_killpoints = cropToRegion(image, roi)
    im_gov_killpoints_gray = cv2.cvtColor(im_gov_killpoints, cv2.COLOR_BGR2GRAY)
    im_gov_killpoints_gray = cv2.bitwise_not(im_gov_killpoints_gray)
    (thresh, im_gov_killpoints_bw) = cv2.threshold(im_gov_killpoints_gray, 100, 255, cv2.THRESH_BINARY)

    gov_name = tk.Tk().clipboard_get()
    roi = (645, 362, 260, 40) #alliance tag
    im_alliance_tag = cropToRegion(image, roi)
    
    #kills tier
    secure_adb_shell(f'input tap 1118 350', device, port)

    #1st image data
    gov_id = pytesseract.image_to_string(im_gov_id_bw,config="--psm 7")
    gov_id = int(re.sub("[^0-9]", "", gov_id))

    gov_power = pytesseract.image_to_string(im_gov_power_bw,config="--psm 7")
    gov_power = int(re.sub("[^0-9]", "", gov_power))

    gov_killpoints = pytesseract.image_to_string(im_gov_killpoints_bw,config="--psm 7")
    gov_killpoints = int(re.sub("[^0-9]", "", gov_killpoints))

    time.sleep(2 + random.random())
    image = secure_adb_screencap(device, port)
    with open(('kills_tier.png'), 'wb') as f:
                f.write(image)  # type: ignore
    image2 = cv2.imread('kills_tier.png')
    image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)
    
    roi = (862, 461, 150, 38) #tier 1
    im_kills_tier1 = cropToRegion(image2, roi)

    roi = (862, 505, 150, 38) #tier 2
    im_kills_tier2 = cropToRegion(image2, roi)

    roi = (862, 549, 150, 38) #tier 3
    im_kills_tier3 = cropToRegion(image2, roi)

    roi = (862, 593, 150, 38) #tier 4
    im_kills_tier4 = cropToRegion(image2, roi)

    roi = (862, 638, 150, 38) #tier 5
    im_kills_tier5 = cropToRegion(image2, roi)

    roi = (1274, 740, 146, 38) #ranged points
    im_ranged_points = cropToRegion(image2, roi)
    im_ranged_points_gray = cv2.cvtColor(im_ranged_points, cv2.COLOR_BGR2GRAY)
    (thresh, im_ranged_points_bw) = cv2.threshold(im_ranged_points_gray, 150, 255, cv2.THRESH_BINARY)

    roi = (1380, 740, 40, 38) #ranged points try 2
    im_ranged_points2 = cropToRegion(image2, roi)
    im_ranged_points2_gray = cv2.cvtColor(im_ranged_points2, cv2.COLOR_BGR2GRAY)
    (thresh, im_ranged_points2_bw) = cv2.threshold(im_ranged_points2_gray, 150, 255, cv2.THRESH_BINARY)

    #More info tab
    secure_adb_shell(f'input tap 387 664', device, port)
    
    #2nd image data
    gov_kills_tier1 = pytesseract.image_to_string(im_kills_tier1,config="--psm 7")
    gov_kills_tier1 = re.sub("[^0-9]", "", gov_kills_tier1)

    gov_kills_tier2 = pytesseract.image_to_string(im_kills_tier2,config="--psm 7")
    gov_kills_tier2 = re.sub("[^0-9]", "", gov_kills_tier2)

    gov_kills_tier3 = pytesseract.image_to_string(im_kills_tier3,config="--psm 7")
    gov_kills_tier3 = re.sub("[^0-9]", "", gov_kills_tier3)

    gov_kills_tier4 = pytesseract.image_to_string(im_kills_tier4,config="--psm 7")
    gov_kills_tier4 = re.sub("[^0-9]", "", gov_kills_tier4)

    gov_kills_tier5 = pytesseract.image_to_string(im_kills_tier5,config="--psm 7")
    gov_kills_tier5 = re.sub("[^0-9]", "", gov_kills_tier5)

    gov_ranged_points = pytesseract.image_to_string(im_ranged_points_bw,config="--psm 7")
    gov_ranged_points = re.sub("[^0-9]", "", gov_ranged_points)

    gov_ranged_points2 = pytesseract.image_to_string(im_ranged_points2_bw,config="--psm 7")
    gov_ranged_points2 = re.sub("[^0-9]", "", gov_ranged_points2)

    time.sleep(1 + random.random())
    image = secure_adb_screencap(device, port)
    with open(('more_info.png'), 'wb') as f:
                f.write(image)  # type: ignore
    image3 = cv2.imread('more_info.png')

    roi = (1130, 443, 183, 40) #dead
    im_dead = cropToRegion(image3, roi)
    roi = (1130, 668, 183, 40) #rss assistance
    im_rss_assistance = cropToRegion(image3, roi)
    roi = (1130, 735, 183, 40) #alliance helps
    im_helps = cropToRegion(image3, roi)
    
    #2nd check for deads with more filters to avoid some errors
    roi = (1130, 443, 183, 40) #dead
    thresh = 127
    thresh_image = cv2.threshold(image3, thresh, 255, cv2.THRESH_BINARY)[1]
    im_dead2 = cropToRegion(thresh_image, roi)
    roi = (1130, 668, 183, 40) #rss assistance
    im_rss_assistance2 = cropToRegion(thresh_image, roi)
    roi = (1130, 735, 183, 40) #alliance helps
    im_helps2 = cropToRegion(thresh_image, roi)
    
    #3rd check for deads with more filters to avoid some errors
    roi = (1130, 443, 183, 40) #dead
    blur_img = cv2.GaussianBlur(image3, (3, 3), 0)
    im_dead3 = cropToRegion(blur_img, roi)
    roi = (1130, 668, 183, 40) #rss assistance
    im_rss_assistance3 = cropToRegion(blur_img, roi)
    roi = (1130, 735, 183, 40) #alliance helps
    im_helps3 = cropToRegion(blur_img, roi)

    #3rd image data
    gov_dead = read_ocr(im_dead)
    gov_dead2 = read_ocr(im_dead2)
    gov_dead3 = read_ocr(im_dead3)
    gov_rss_assistance = read_ocr(im_rss_assistance)
    gov_rss_assistance2 = read_ocr(im_rss_assistance2)
    gov_rss_assistance3 = read_ocr(im_rss_assistance3)
    gov_helps = read_ocr(im_helps)
    gov_helps2 = read_ocr(im_helps2)
    gov_helps3 = read_ocr(im_helps3)

    #alliance tag
    gray = cv2.cvtColor(im_alliance_tag,cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (0, 0), fx=3, fy=3)
    alliance_image_raw = Image.fromarray(gray)
    alliance_image_raw.save("alliance-raw.jpeg")
    #threshold_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    gray_blur = cv2.GaussianBlur(gray, (3, 3), 0)
    threshold_img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 9, 0)
    alliance_image = Image.fromarray(threshold_img)
    alliance_image.save("alliance.jpeg")

    dilation_element = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    erosion_element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated_img = cv2.dilate(threshold_img, dilation_element)
    erosion_img = cv2.erode(dilated_img, erosion_element)

    alliance_image_dilated = Image.fromarray(erosion_img)
    alliance_image_dilated.save("alliance-eroded.jpeg")
    #threshold_img = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    alliance_tag = pytesseract.image_to_string(erosion_img, config='--psm 13 --oem 1')

    #Just to check the progress, printing in cmd the result for each governor
    if gov_power == '':
        gov_power = 'Unknown'
    if gov_killpoints =='':
        gov_killpoints = 'Unknown'
    if gov_dead == '' :
        if gov_dead2 == '':
            if gov_dead3 =='':
                gov_dead = 'Unknown'
            else:			
                gov_dead = gov_dead3
        else:
            gov_dead = gov_dead2
    if gov_kills_tier1 == '' :
        gov_kills_tier1 = 'Unknown'
    if gov_kills_tier2 == '' :
        gov_kills_tier2 = 'Unknown'
    if gov_kills_tier3 == '' :
        gov_kills_tier3 = 'Unknown'
    if gov_kills_tier4 == '' :
        gov_kills_tier4 = 'Unknown'
    if gov_kills_tier5 == '' :
        gov_kills_tier5 = 'Unknown'
    if gov_ranged_points == '':
        if gov_ranged_points2 == '':
            gov_ranged_points = "Unknown"
        else:
            gov_ranged_points = gov_ranged_points2
    if gov_rss_assistance == '' :
        if gov_rss_assistance2 =='':
            if gov_rss_assistance3 =='':
                gov_rss_assistance = 'Unknown'
            else: 
                gov_rss_assistance = gov_rss_assistance3
        else:
            gov_rss_assistance= gov_rss_assistance2
    if gov_helps == '' :
        if gov_helps2 =='':
            if gov_helps3 =='':
                gov_helps = 'Unknown'
            else: 
                gov_helps = gov_helps3
        else:
            gov_helps = gov_helps2

    gov_kills_tier45 = to_int_check(gov_kills_tier4) + to_int_check(gov_kills_tier5)
    gov_kills_total = to_int_check(gov_kills_tier1) + to_int_check(gov_kills_tier2) + to_int_check(gov_kills_tier3) + gov_kills_tier45

    secure_adb_shell(f'input tap 1396 58', device, port) #close more info
    time.sleep(0.5 + random.random())
    secure_adb_shell(f'input tap 1365 104', device, port) #close governor info
    time.sleep(2 + random.random())

    return {
        "id": gov_id,
        "name": gov_name,
        "power": gov_power,
        "killpoints": gov_killpoints,
        "kills_t1": gov_kills_tier1,
        "kills_t2": gov_kills_tier2,
        "kills_t3": gov_kills_tier3,
        "kills_t4": gov_kills_tier4,
        "kills_t5": gov_kills_tier5,
        "kills_t45": gov_kills_tier45,
        "kills_total": gov_kills_total,
        "ranged_points": gov_ranged_points,
        "dead": gov_dead,
        "rss_assistance": gov_rss_assistance,
        "helps": gov_helps,
        "alliance": alliance_tag,
        "inactives": inactive_players
    }

def scan(port: int, kingdom: str, amount: int, resume: bool, track_inactives: bool):
    #Initialize the connection to adb
    device = start_adb(port)

    ######Excel Formatting
    wb = Workbook()
    sheet1 = wb.active
    sheet1.title = str(datetime.date.today())

    #Make Head Bold
    font = Font(bold=True)

    #Initialize Excel Sheet Header
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

    #Counter for fails
    inactive_players = 0

    #Positions for next governor to check
    Y =[285, 390, 490, 590, 605, 705, 805]

    #Resume Scan options. Refine the loop
    j = 0
    if resume:
        j = 4
        amount = amount + j
    #The loop in TOP XXX Governors in kingdom - It works both for power and killpoints Rankings
    #MUST have the tab opened to the 1st governor(Power or Killpoints)

    stop = False

    for i in range(j,amount):
        if stop:
            console.print("Scan Terminated! Saving the current progress...")
            break
        if i == 998:
            k = 5
        if i == 999:
            k = 6
        else:
            if i > 4:
                k = 4
            else:
                k = i

        governor = governor_scan(device, port, Y[k], inactive_players, track_inactives)
        inactive_players = governor["inactives"]

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")

        # nice output for console
        table = Table(title='[' + current_time + ']\n' + "Latest Scan Result\nGovernor " + str(i + 1) + ' of ' + str(amount), show_header=True, show_footer=True)
        table.add_column("Entry", "Approx time remaining\nSkipped", style="magenta")
        table.add_column("Value", str(datetime.timedelta(seconds=(amount - i) * 19)) + "\n" + str(inactive_players), style="cyan")

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
        table.add_row("Governor Helps", str(governor["helps"]))
        table.add_row("Governor Alliance", governor["alliance"].rstrip())

        console.print(table)

        expectedKp = math.floor(to_int_check(governor["kills_t1"]) * 0.2) \
                        + (to_int_check(governor["kills_t2"]) * 2) \
                        + (to_int_check(governor["kills_t3"]) * 4) \
                        + (to_int_check(governor["kills_t4"]) * 10) \
                        + (to_int_check(governor["kills_t5"]) * 20)
        killsOk = expectedKp == to_int_check(governor["killpoints"])
        console.print('Kills check out: ', killsOk)

        if(not killsOk):
             logging.log(logging.WARNING, f'''Kills for {governor["name"]} ({to_int_check(governor["id"])}) don't check out, manually need to look at them!''')

        #Write results in excel file
        sheet1["A" + str(i+2-j)] = to_int_check(governor["id"])
        sheet1["B" + str(i+2-j)] = governor["name"]
        sheet1["C" + str(i+2-j)] = to_int_check(governor["power"])
        sheet1["D" + str(i+2-j)] = to_int_check(governor["killpoints"])
        sheet1["E" + str(i+2-j)] = to_int_check(governor["dead"])
        sheet1["F" + str(i+2-j)] = to_int_check(governor["kills_t1"])
        sheet1["G" + str(i+2-j)] = to_int_check(governor["kills_t2"])
        sheet1["H" + str(i+2-j)] = to_int_check(governor["kills_t3"])
        sheet1["I" + str(i+2-j)] = to_int_check(governor["kills_t4"])
        sheet1["J" + str(i+2-j)] = to_int_check(governor["kills_t5"])
        sheet1["K" + str(i+2-j)] = to_int_check(governor["kills_total"])
        sheet1["L" + str(i+2-j)] = to_int_check(governor["kills_t45"])
        sheet1["M" + str(i+2-j)] = to_int_check(governor["rss_assistance"])
        sheet1["N" + str(i+2-j)] = to_int_check(governor["helps"])
        sheet1["O" + str(i+2-j)] = governor["alliance"].rstrip()
        sheet1["P" + str(i+2-j)] = to_int_check(governor["ranged_points"])

        if resume :
            file_name_prefix = 'NEXT'
        else:
            file_name_prefix = 'TOP'
        wb.save(file_name_prefix + str(amount-j) + '-' +str(datetime.date.today())+ '-' + kingdom +'.xlsx')
    if resume :
        file_name_prefix = 'NEXT'
    else:
        file_name_prefix = 'TOP'
    wb.save(file_name_prefix + str(amount-j) + '-' +str(datetime.date.today())+ '-' + kingdom +'.xlsx')
    return


def main():
    signal.signal(signal.SIGINT, stopHandler)
    port = IntPrompt.ask("Adb port of device", default=get_bluestacks_port())
    kingdom = Prompt.ask("Kingdom name (used for file name)", default="KD")
    scan_amount = IntPrompt.ask("People to scan", default=600)
    resume_scan = Confirm.ask("Resume scan", default=False)
    track_inactives = Confirm.ask("Track inactives (via screenshot)", default=False)
    scan(port, kingdom, scan_amount, resume_scan, track_inactives)

    exit(1)

if __name__ == "__main__":
    main()