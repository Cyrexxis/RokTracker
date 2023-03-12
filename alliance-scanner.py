from rich.prompt import Prompt
from rich.prompt import IntPrompt
from rich.prompt import Confirm
from rich.console import Console
from rich.table import Table
from ppadb.client import Client
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.drawing.image import Image as OpImage
from pathlib import Path
from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator
import configparser
import subprocess
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

mode_data = {
     "Alliance": {
        "name": (334, 260, 293, 33),
        "score": (1117, 265, 250, 33),
        "threshold": 90,
        "invert": True,
        "script": "./inputs/alliance_1_person_scroll.txt"
     },
     "Honor": {
        "name": (774, 330, 257, 33),
        "score": (1183, 330, 178, 33),
        "threshold": 150,
        "invert": False,
        "script": "./inputs/honor_1_person_scroll.txt"
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
    result = ""
    for i in range(3):
        try:
            result = device.shell(command_to_execute)
        except:
            console.print("[red]ADB crashed[/red]")
            device = start_adb(port)
        else:
            return result

def adb_send_events(input_device_name, event_file, device, port):
    idn = secure_adb_shell(f"getevent -pl 2>&1 | sed -n '/^add/{{h}}/{input_device_name}/{{x;s/[^/]*//p}}'", device, port)
    idn = str(idn).strip()
    macroFile = open(event_file, 'r')
    lines = macroFile.readlines()

    for line in lines:
            secure_adb_shell(f'''sendevent {idn} {line.strip()}''', device, port)

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
    gov_name = ""
    gov_score = 0
    
    # Take screenshot to process
    image = secure_adb_screencap(device, port)
    with open(('currentState.png'), 'wb') as f:
                f.write(image)  # type: ignore
    image = cv2.imread('currentState.png')

    #Power and Killpoints
    im_gov_name = cropToRegion(image, mode_data[mode]["name"])
    im_gov_name_bw = preprocessImage(im_gov_name, 3, mode_data[mode]["threshold"], 12, mode_data[mode]["invert"])
    im_gov_name_bw_small = preprocessImage(im_gov_name, 1, mode_data[mode]["threshold"], 4, mode_data[mode]["invert"])
    cv2.imwrite("tmp/gov_name" + str(gov_number) + ".png", im_gov_name_bw_small)

    image = cv2.imread('currentState.png')
    im_gov_score = cropToRegion(image, mode_data[mode]["score"])
    im_gov_score_bw = preprocessImage(im_gov_score, 3, mode_data[mode]["threshold"], 12, mode_data[mode]["invert"])
    
    #gov_name = pytesseract.image_to_string(im_gov_name,config="--oem 1 -l ara+chi_sim+chi_tra+deu+ell+grc+hat+hrv+heb+hin+ind+jpn+kor+lao+mal+mon+rus+san+swa+tha+tur+vie")
    gov_name = pytesseract.image_to_string(im_gov_name_bw, config="--oem 1 --psm 7 -l eng")
    gov_score = pytesseract.image_to_string(im_gov_score_bw, config="--oem 1 --psm 8")
    
    gov_score = int(re.sub("[^0-9]", "", gov_score))

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
        if stop:
            console.print("Scan Terminated! Saving the current progress...")
            break

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

        adb_send_events("Touch", mode_data[mode]["script"], device, port)
        
        time.sleep(1 + random.random())
    if resume :
        file_name_prefix = 'NEXT'
    else:
        file_name_prefix = 'TOP'
    wb.save(file_name_prefix + str(amount) + '-' +str(datetime.date.today())+ '-' + kingdom +'.xlsx')
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