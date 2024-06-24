from typing import Tuple
from roktracker.utils.console import console
from PIL.Image import Image, new as NewImage
from com.dtmilano.android.adb.adbclient import AdbClient
from pathlib import Path
import subprocess
import socket
import configparser
import sys

from roktracker.utils.exceptions import AdbError
from roktracker.utils.general import to_int_or


def get_bluestacks_port(bluestacks_device_name: str, config) -> int:
    default_port = to_int_or(config["general"]["adb_port"], 5555)
    # try to read port from bluestacks config
    if config["general"]["emulator"] == "bluestacks":
        try:
            dummy = "AmazingDummy"
            with open(config["general"]["bluestacks"]["config"], "r") as config_file:
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
    return default_port


class AdvancedAdbClient:
    def __init__(
        self,
        adb_path: str,
        port: int,
        player: str,
        script_base: str | Path,
        start_immediately=False,
    ):
        self.server_port = 0
        self.client_port = port
        self.adb_path = adb_path
        self.started = start_immediately
        self.player = player
        self.script_base = Path(script_base)

        if start_immediately:
            self.start_adb()

    def get_free_port(self) -> int:
        s = socket.socket()
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def set_adb_path(self, path: str) -> None:
        self.adb_path = path

    def kill_adb(self) -> None:
        console.print("Killing ADB server...")
        process = subprocess.run(
            [self.adb_path, "-P " + str(self.server_port), "kill-server"],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        console.print(process.stdout)

    def start_adb(self) -> None:
        self.server_port = self.get_free_port()
        console.print("Starting adb server and connecting to adb device...")
        process = subprocess.run(
            [
                self.adb_path,
                "-P " + str(self.server_port),
                "connect",
                "localhost:" + str(self.client_port),
            ],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        console.print(process.stdout)
        try:
            adb_client = AdbClient(
                serialno=".*", hostname="localhost", port=self.server_port
            )
        except RuntimeError as error:
            console.log("No device connected, aborting.")
            self.kill_adb()
            raise AdbError(str(error))
        self.device = adb_client

    def secure_adb_shell(self, command_to_execute: str) -> str:
        result = ""
        for i in range(3):
            try:
                result = str(self.device.shell(command_to_execute))
            except:
                console.print("[red]ADB crashed[/red]")
                self.kill_adb()
                self.start_adb()
            else:
                return result
        return result

    def secure_adb_tap(self, position: Tuple[int, int]):
        self.secure_adb_shell(f"input tap {position[0]} {position[1]}")

    def secure_adb_screencap(self) -> Image:
        result = NewImage(mode="RGB", size=(1, 1))
        for i in range(3):
            try:
                result = self.device.takeSnapshot(reconnect=True)
            except:
                console.print("[red]ADB crashed[/red]")
                self.kill_adb()
                self.start_adb()
            else:
                return result
        return result

    def adb_send_events(self, input_device_name: str, event_file: str | Path) -> None:
        if input_device_name == "Touch":
            if self.player == "ld":
                input_device_name = "ABS_MT_POSITION_Y"

        idn = self.secure_adb_shell(
            f"getevent -pl 2>&1 | sed -n '/^add/{{h}}/{input_device_name}/{{x;s/[^/]*//p}}'",
        )
        idn = str(idn).strip()
        macroFile = open(self.script_base / self.player / event_file, "r")
        lines = macroFile.readlines()

        for line in lines:
            self.secure_adb_shell(f"""sendevent {idn} {line.strip()}""")
