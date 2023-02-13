from rich.prompt import Prompt
from rich.prompt import IntPrompt
from rich.prompt import Confirm
from rich.console import Console
from rich.table import Table
from ppadb.client import Client
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.drawing.image import Image as OpImage
import configparser
import subprocess
import datetime
import time
import random
import cv2
import pytesseract
import signal
import os

console = Console()

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

def governor_scan(device, port: int, gov_number: int):
    # set up the scan variables
    gov_name = ""
    gov_score = 0
    
    # Take screenshot to process
    image = secure_adb_screencap(device, port)
    with open(('currentState.png'), 'wb') as f:
                f.write(image)  # type: ignore
    image = cv2.imread('currentState.png')

    #Power and Killpoints
    roi = (334, 260, 293, 33)
    im_gov_name = image[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
    im_gov_name_gray = cv2.cvtColor(im_gov_name, cv2.COLOR_BGR2GRAY)
    im_gov_name_gray = cv2.bitwise_not(im_gov_name_gray)
    (thresh, im_gov_name_bw) = cv2.threshold(im_gov_name_gray, 90, 255, cv2.THRESH_BINARY)
    cv2.imwrite("tmp/gov_name" + str(gov_number) + ".png", im_gov_name_bw)

    image = cv2.imread('currentState.png')
    #image = cv2.GaussianBlur(image, (5, 5), 0)
    roi = (1117, 265, 250, 33)
    im_gov_score = image[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
    
    #gov_name = pytesseract.image_to_string(im_gov_name,config="--oem 1 -l ara+chi_sim+chi_tra+deu+ell+grc+hat+hrv+heb+hin+ind+jpn+kor+lao+mal+mon+rus+san+swa+tha+tur+vie")
    gov_name = pytesseract.image_to_string(im_gov_name_bw, config="--oem 1 --psm 7 -l ara+chi_sim+eng+jpn+kor+rus+tha+vie")
    gov_score = pytesseract.image_to_string(im_gov_score, config="--oem 1 -c tessedit_char_whitelist=0123456789")

    #Just to check the progress, printing in cmd the result for each governor
    if gov_score == '':
        gov_score = 'Unknown'

    return {
        "name": gov_name,
        "score": gov_score
    }

def scan(port: int, kingdom: str, amount: int, resume: bool):
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

    os.mkdir("tmp")

    for i in range(0,amount):
        if stop:
            console.print("Scan Terminated! Saving the current progress...")
            break

        governor = governor_scan(device, port, i)

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
        sheet1.add_image(OpImage("tmp/gov_name" + str(i) + ".png"), "A" + str(i+2))
        sheet1["B" + str(i+2)] = governor["name"]
        sheet1["C" + str(i+2)] = to_int_check(governor["score"])

        if resume :
            file_name_prefix = 'NEXT'
        else:
            file_name_prefix = 'TOP'
        wb.save(file_name_prefix + str(amount) + '-' +str(datetime.date.today())+ '-' + kingdom +'.xlsx')

        secure_adb_shell(f'input swipe 690 605 690 501 4000', device, port)
        time.sleep(1 + random.random())
    if resume :
        file_name_prefix = 'NEXT'
    else:
        file_name_prefix = 'TOP'
    wb.save(file_name_prefix + str(amount) + '-' +str(datetime.date.today())+ '-' + kingdom +'.xlsx')
    return


def main():
    signal.signal(signal.SIGINT, stopHandler)
    port = IntPrompt.ask("Adb port of device", default=get_bluestacks_port())
    kingdom = Prompt.ask("Kingdom name", default="2414")
    scan_amount = IntPrompt.ask("People to scan", default=600)
    resume_scan = Confirm.ask("Resume scan", default=False)
    scan(port, kingdom, scan_amount, resume_scan)

    exit(1)

if __name__ == "__main__":
    main()