from console import console
from PIL.Image import Image, new as NewImage
from com.dtmilano.android.adb.adbclient import AdbClient
from pathlib import Path
import subprocess
import socket

adb_server_port = 0
device: AdbClient

def get_free_port():
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def kill_adb():
    console.print("Killing ADB server...")
    process = subprocess.run(['.\\platform-tools\\adb.exe', '-P ' + str(adb_server_port), 'kill-server'], 
                         stdout=subprocess.PIPE, 
                         universal_newlines=True)
    console.print(process.stdout)

def start_adb(port: int):
    global adb_server_port
    global device
    adb_server_port = get_free_port()
    console.print("Starting adb server and connecting to adb device...")
    process = subprocess.run(['.\\platform-tools\\adb.exe', '-P ' + str(adb_server_port), 'connect',  'localhost:' + str(port)], 
                         stdout=subprocess.PIPE, 
                         universal_newlines=True)
    console.print(process.stdout)
    try:
        adb_client = AdbClient(serialno=".*", hostname='localhost', port=adb_server_port)
    except:
         console.log("No device connected, aborting.")
         kill_adb()
         exit(0)
    device = adb_client

def secure_adb_shell(command_to_execute: str, port: int) -> str:
    result = ""
    for i in range(3):
        try:
            result = str(device.shell(command_to_execute))
        except:
            console.print("[red]ADB crashed[/red]")
            kill_adb()
            start_adb(port)
        else:
            return result
    return result

def secure_adb_screencap(port: int) -> Image:
    result = NewImage(mode="RGB", size=(1,1))
    for i in range(3):
        try:
            result = device.takeSnapshot(reconnect=True)
        except:
            console.print("[red]ADB crashed[/red]")
            kill_adb()
            start_adb(port)
        else:
            return result
    return result

def adb_send_events(input_device_name: str, event_file: str | Path, port: int):
    idn = secure_adb_shell(f"getevent -pl 2>&1 | sed -n '/^add/{{h}}/{input_device_name}/{{x;s/[^/]*//p}}'", port)
    idn = str(idn).strip()
    macroFile = open(event_file, 'r')
    lines = macroFile.readlines()

    for line in lines:
            secure_adb_shell(f'''sendevent {idn} {line.strip()}''', port)