from console import console
from adbutils import *
from rich.prompt import Confirm
from rich.console import Console
from rich.table import Table
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.drawing.image import Image as OpImage
from pathlib import Path
from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator
import configparser
import datetime
import time
import random
import cv2
import pytesseract
import signal
import re

# this is needed due to not yet published fix from InquirerPy
#pyright: reportPrivateImportUsage=false

console = Console()
scan_index = 0
reached_bottom = False
abort_scan = False

mode_data = {
     "Alliance": {
        "name": (334, 260, 293, 33),
        "score": (1117, 265, 250, 33),
        "threshold": 90,
        "invert": True,
        "script": "./inputs/alliance_1_person_scroll.txt",
        "name_pos": [(334, 260, 293, 33),
                     (334, 283, 293, 33),
                     (334, 383, 293, 33),
                     (334, 483, 293, 33),
                     (334, 595, 293, 33),
                     (334, 685, 293, 33),
                     (334, 785, 293, 33)],
        "score_pos": [(1117, 265, 250, 33),
                      (1117, 288, 250, 33),
                      (1117, 388, 250, 33),
                      (1117, 488, 250, 33),
                      (1117, 590, 250, 33),
                      (1117, 690, 250, 33),
                      (1117, 790, 250, 33)]
     },
     "Honor": {
        "name": (774, 330, 257, 33),
        "score": (1183, 330, 178, 33),
        "threshold": 150,
        "invert": False,
        "script": "./inputs/honor_1_person_scroll.txt",
        "name_pos": [(774, 330, 257, 33),
                     (774, 424, 257, 33),
                     (774, 524, 257, 33),
                     (774, 624, 257, 33),
                     (774, 724, 257, 33)],
        "score_pos": [(1183, 330, 178, 33),
                      (1183, 424, 178, 33),
                      (1183, 524, 178, 33),
                      (1183, 624, 178, 33),
                      (1183, 724, 178, 33)]
     }
}

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

def to_int_check(element):
	try:
		return int(element)
	except ValueError:
		#return element
		return int(0)

def stopHandler(signum, frame):
    global abort_scan
    stop = Confirm.ask("Do you really want to exit?")
    if stop:
        console.print("Scan will aborted after next governor.")
        abort_scan = True

def cropToRegion(image, roi):
     return image[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

def cropToTextWithBorder(img, border_size):
    coords = cv2.findNonZero(cv2.bitwise_not(img))
    x, y, w, h = cv2.boundingRect(coords)

    roi = img[y:y+h, x:x+w]
    bordered = cv2.copyMakeBorder(roi, top=border_size, bottom=border_size, left=border_size, right=border_size, borderType=cv2.BORDER_CONSTANT, value=255)
    
    return bordered

def preprocessImage(image, scale_factor, threshold, border_size, invert = False):
    im_big = cv2.resize(image, (0, 0), fx=scale_factor, fy=scale_factor)
    im_gray = cv2.cvtColor(im_big, cv2.COLOR_BGR2GRAY)
    if invert:
        im_gray = cv2.bitwise_not(im_gray)
    (thresh, im_bw) = cv2.threshold(im_gray, threshold, 255, cv2.THRESH_BINARY)
    im_bw = cropToTextWithBorder(im_bw, border_size)
    return im_bw

def governor_scan(mode:str, device, port: int, gov_number: int):
    # set up the scan variables
    global scan_index
    global reached_bottom
    gov_name = ""
    gov_score = 0
    tries = 0
    max_tries = 3
    
    if reached_bottom:
         scan_index = scan_index + 1
         if scan_index >= len(mode_data[mode]["name_pos"]):
              console.log("Last governor scanned, scan completed.")
              exit(0)

    # Take screenshot to process
    secure_adb_screencap(device, port).save('currentState.png')
    image = cv2.imread('currentState.png')

    #Power and Killpoints
    while tries < max_tries:
        # needed for detection in alliance mode
        try:
            im_gov_name = cropToRegion(image, mode_data[mode]["name_pos"][scan_index])
            im_gov_name_bw = preprocessImage(im_gov_name, 3, mode_data[mode]["threshold"], 12, mode_data[mode]["invert"])
            im_gov_name_bw_small = preprocessImage(im_gov_name, 1, mode_data[mode]["threshold"], 4, mode_data[mode]["invert"])
            cv2.imwrite("tmp/gov_name" + str(gov_number) + ".png", im_gov_name_bw_small)

            image = cv2.imread('currentState.png')
            im_gov_score = cropToRegion(image, mode_data[mode]["score_pos"][scan_index])
            im_gov_score_bw = preprocessImage(im_gov_score, 3, mode_data[mode]["threshold"], 12, mode_data[mode]["invert"])
            
            #gov_name = pytesseract.image_to_string(im_gov_name,config="--oem 1 -l ara+chi_sim+chi_tra+deu+ell+grc+hat+hrv+heb+hin+ind+jpn+kor+lao+mal+mon+rus+san+swa+tha+tur+vie")
            gov_name = pytesseract.image_to_string(im_gov_name_bw, config="--oem 1 --psm 7 -l eng")
            gov_score = pytesseract.image_to_string(im_gov_score_bw, config="--oem 1 --psm 8")
            
            gov_score = int(re.sub("[^0-9]", "", gov_score))
            break
        except:
            if not reached_bottom:
                tries = tries + 1
                scan_index = scan_index + 1
                reached_bottom = True
                console.log("Didn't find score, assuming bottom is reached. Starting scan of last 6 governors.")
            else:
                console.log("Aborting scan, because an error occurred.")
                exit(0)

    #Just to check the progress, printing in cmd the result for each governor
    if gov_score == '':
        gov_score = 'Unknown'

    return {
        "name": gov_name,
        "score": gov_score
    }

def scan(port: int, kingdom: str, mode: str, amount: int, resume: bool):
    #Initialize the connection to adb
    device = start_adb(port)

    ######Excel Formatting
    wb = Workbook()
    sheet1 = wb.active
    sheet1.title = str(datetime.date.today())

    #Make Head Bold
    font = Font(bold=True)

    #Initialize Excel Sheet Header
    sheet1["A1"] = "Name Image"
    sheet1["B1"] = "Governor Name"
    sheet1["C1"] = "Governor Score"

    sheet1.column_dimensions["A"].width = 42
    sheet1["A1"].font = font
    sheet1["B1"].font = font
    sheet1["C1"].font = font

    stop = False

    Path('./tmp').mkdir(parents=True, exist_ok=True)

    for i in range(0,amount):
        if abort_scan:
            console.print("Scan Terminated! Saving the current progress...")
            break

        governor = governor_scan(mode, device, port, i)

        # needed for detection of end in honor mode
        if sheet1["B" + str(i+1)].value == governor["name"] and sheet1["C" + str(i+1)].value == to_int_check(governor["score"]):
             global reached_bottom
             reached_bottom = True
             console.log("Duplicate governor, switching to scan of last governors")
             governor = governor_scan(mode, device, port, i)

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")

        # nice output for console
        table = Table(title='[' + current_time + ']\n' + "Latest Scan Result\nGovernor " + str(i + 1) + ' of ' + str(amount), show_header=True, show_footer=True)
        table.add_column("Entry", "Approx time remaining\nSkipped", style="magenta")
        table.add_column("Value", str(datetime.timedelta(seconds=(amount - i) * 6)), style="cyan")

        table.add_row("Governor Name", governor["name"])
        table.add_row("Governor Score", str(governor["score"]))

        console.print(table)

        sheet1.row_dimensions[i+2].height = 24.75
        #Write results in excel file
        image = OpImage("tmp/gov_name" + str(i) + ".png")
        sheet1.add_image(OpImage("tmp/gov_name" + str(i) + ".png"), "A" + str(i+2))
        sheet1["B" + str(i+2)] = governor["name"]
        sheet1["C" + str(i+2)] = to_int_check(governor["score"])

       

        if resume :
            file_name_prefix = 'NEXT'
        else:
            file_name_prefix = 'TOP'
        wb.save(file_name_prefix + str(amount) + '-' +str(datetime.date.today())+ '-' + kingdom +'.xlsx')

        if not reached_bottom:
            adb_send_events("Touch", mode_data[mode]["script"], device, port)
        
        time.sleep(1 + random.random())
    if resume :
        file_name_prefix = 'NEXT'
    else:
        file_name_prefix = 'TOP'
    wb.save(file_name_prefix + str(amount) + '-' +str(datetime.date.today())+ '-' + kingdom +'.xlsx')
    kill_adb() # make sure to clean up adb server
    return


def main():
    signal.signal(signal.SIGINT, stopHandler)

    port = inquirer.text(message=f"Adb port of your device:", default=str(get_bluestacks_port()), validate=NumberValidator()).execute()
    kingdom = inquirer.text(message="Alliance name:", default="Alliance").execute()
    mode = inquirer.select(message="What do you want to scan:", choices=["Alliance", "Honor"], default="Alliance").execute()
    scan_amount = inquirer.text(message="People to scan:", default="150", validate=NumberValidator()).execute()
    resume_scan = inquirer.confirm(message="Resume scan:", default=False).execute()

    scan(int(port), kingdom, mode, int(scan_amount), resume_scan)

    exit(1)

if __name__ == "__main__":
    main()