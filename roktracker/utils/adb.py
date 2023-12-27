from typing import Tuple
from roktracker.utils.console import console
from PIL.Image import Image, new as NewImage
from com.dtmilano.android.adb.adbclient import AdbClient
from pathlib import Path
import subprocess
import socket
import configparser
import sys

adb_server_port = 0
device: AdbClient
adb_path = ".\\platform-tools\\adb.exe"


def get_bluestacks_port(bluestacks_device_name, config):
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


def get_free_port():
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def set_adb_path(path: str):
    global adb_path
    adb_path = path


def kill_adb():
    console.print("Killing ADB server...")
    process = subprocess.run(
        [adb_path, "-P " + str(adb_server_port), "kill-server"],
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    console.print(process.stdout)


def start_adb(port: int):
    global adb_server_port
    global device
    adb_server_port = get_free_port()
    console.print("Starting adb server and connecting to adb device...")
    process = subprocess.run(
        [adb_path, "-P " + str(adb_server_port), "connect", "localhost:" + str(port)],
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    console.print(process.stdout)
    try:
        adb_client = AdbClient(
            serialno=".*", hostname="localhost", port=adb_server_port
        )
    except:
        console.log("No device connected, aborting.")
        kill_adb()
        sys.exit(0)
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


def secure_adb_tap(position: Tuple[int, int], port: int):
    secure_adb_shell(f"input tap {position[0]} {position[1]}", port)


def secure_adb_screencap(port: int) -> Image:
    result = NewImage(mode="RGB", size=(1, 1))
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
    idn = secure_adb_shell(
        f"getevent -pl 2>&1 | sed -n '/^add/{{h}}/{input_device_name}/{{x;s/[^/]*//p}}'",
        port,
    )
    idn = str(idn).strip()
    macroFile = open(event_file, "r")
    lines = macroFile.readlines()

    for line in lines:
        secure_adb_shell(f"""sendevent {idn} {line.strip()}""", port)
