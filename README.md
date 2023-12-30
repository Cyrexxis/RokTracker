# RokTracker

**Version 3 is now released! The biggest new feature is a brand new graphical user interface as well as better configurability. The alliance and honor scan scripts are currently not maintained and are still the same as version 1.**

> [!IMPORTANT]  
> There are now two ways to run the scanner. One way is to download the compiled exe file and the other is the old way to run the python script manually. Also, you will have to move some of the dependencies to a different folder if you are updating.

Open Source Rise of Kingdoms Stats Management Tool. Track TOP X Players in kingdom / alliance / honor leaderboard. Depending on what you scan the resulting .xlsx will look different:

For kingdom rankings Governor Id, Governor Name, Power, Kill Points, Ranged Points, T1/T2/T3/T4/T5 Kills, Total kills, T4+T5 kills, Dead troops, RSS Gathered, RSS Assistance, Helps and Alliance name will get saved.

For the honor and alliance rankings only the governor name and the score will be saved. Because there is no guarantee that the name is correct a picture of the name will be saved in addition.

This is a heavily modified version of the original tool from [nikolakis1919](https://github.com/nikolakis1919) in the repository [https://github.com/nikolakis1919/RokTracker](https://github.com/nikolakis1919/RokTracker)

# Simple installation (with or without GUI)

## Required

1. Bluestacks 5 Installation [https://www.bluestacks.com/de/bluestacks-5.html](https://www.bluestacks.com/de/bluestacks-5.html)
2. To use tesserocr you also need to download the trained tesseract models [https://github.com/tesseract-ocr/tessdata](https://github.com/tesseract-ocr/tessdata)
3. Adb Platform Tools Download and Extract(See Important Notes) [https://dl.google.com/android/repository/platform-tools_r31.0.3-windows.zip](https://dl.google.com/android/repository/platform-tools_r31.0.3-windows.zip)
4. Tested on Windows 10 and 11, could work on Windows 7

## Setup

1. Download the latest release for your system here: [Latest Release](https://github.com/Cyrexxis/RokTracker/releases/latest) (choose the console or GUI version)
2. Extract the zip in the folder where you want the scanner to be installed in
3. Download the requirements 2 (tessdata) and 3 (platform-tools) and extract them in the deps folder
4. Configure your Bluestacks instance according to the [instructions](#bluestacks-5-settings)

## Usage

1. Adjust the default options in the `config.json` file to your liking
2. Double-click the exe like any normal program and enjoy the scanner
3. The results of the scans can be found in the `scans` folder

## Folder/File Structure

```
./
├─ _internal/
│ ├─ ...
├─ deps/
│ ├─ inputs/
│ ├─ tessdata/
│ │ ├─ *.traineddata
│ │ ├─ ...
│ ├─ platform-tools/
│ │ ├─ adb.exe
│ │ ├─ ...
├─ config.json
├─ RoK Tracker.exe
```

# Advanced installation (with or without GUI)

## Required

1. Bluestacks 5 Installation [https://www.bluestacks.com/de/bluestacks-5.html](https://www.bluestacks.com/de/bluestacks-5.html)
2. Python 3.11 Installation [https://www.python.org/downloads/release/python-3110/](https://www.python.org/downloads/release/python-3110/)
3. To use tesserocr you also need to download the trained tesseract models [https://github.com/tesseract-ocr/tessdata](https://github.com/tesseract-ocr/tessdata)
4. Adb Platform Tools Download and Extract(See Important Notes) [https://dl.google.com/android/repository/platform-tools_r31.0.3-windows.zip](https://dl.google.com/android/repository/platform-tools_r31.0.3-windows.zip)
5. On Windows "Microsoft Build Tools für C++" might be required for some of the python packages [https://visualstudio.microsoft.com/de/visual-cpp-build-tools/](https://visualstudio.microsoft.com/de/visual-cpp-build-tools/)
6. Tested on Windows 10 and 11, could work on Windows 7. Tested with Python 3.11.0 and 3.11.7.

## Setup

1. Download the latest release for your system here: [Latest Release](https://github.com/Cyrexxis/RokTracker/releases/latest) (choose the source code option)
2. Download and install Python and Build Tools for C++
3. Download the requirements 3 (tessdata) and 4 (platform-tools) and extract them in the deps folder
4. Open your terminal in this folder and create a venv via `python -m venv venv`
5. Activate that venv via `./venv/Scripts/activate`
6. Install the python requirements via `pip install -r requirements_win64.txt`
7. Configure your Bluestacks instance according to the [instructions](#bluestacks-5-settings)

## Usage

1. Open a terminal in your rok tracker folder
2. Activate the venv via `./venv/Scripts/activate`
3. Start the scanner either with `python rok_scanner.py` for the console version or with `python graphics_scanner.py` for the GUI version
4. The results of the scans can be found in the `scans` folder

As an alternative you can also simply double-click either `run_scanner.bat` for the console version or `run_scanner_ui.bat` for the GUI version.

## Folder/File Structure

```
./
├─ deps/
│ ├─ inputs/
│ ├─ tessdata/
│ │ ├─ *.traineddata
│ │ ├─ ...
│ ├─ platform-tools/
│ │ ├─ adb.exe
│ │ ├─ ...
├─ config.json
├─ rok_scanner.py
├─ graphic_scanner.py
├─ run_scanner.bat
├─ ...
```

# Features

## RoK Tracker

- Complete kingdom ranking scan
- Detection for wrong kills based on if kills to kill points are correct
  - In case something doesn't check out the corresponding images are saved in the `manual_review`-folder (prefix F) and a warning is logged in the log file.
- Option to try to recover kills if wrong kills are detected
  - Nevertheless the same images as for a fail get copied to the `manual_review`-folder (prefix R) and an info is logged in the log file.
- Detection of inactive accounts
  - an inactive account is an account that cannot be clicked in the kingdom rankings
  - those are skipped automatically, and it is optionally possible to save a screenshot of the name in the `inactives`-folder.

## Alliance Scanner (currently unmaintained)

- complete alliance ranking scan
- complete personal honor ranking scan
- due to how the game works the names are very inaccurate, and it is not possible to track the governor id

# Bluestacks 5 Settings

- Display Tab ([Screenshot](images/bluestacks-display.png))
  - Resolution: 1600x900
  - DPI: Custom (450)
- Advanced Tab ([Screenshot](images/bluestacks-advanced.png))
  - Android Debug Bride: Turned on

The scanner script tries to find the current debugging port by reading the bluestacks config. For that to work the emulator used for scanning should have the instance name "RoK Tracker" and you need to change the config location in the config.json file to match your Bluestacks installation. If the auto-detect fails it will default to 5555, and you can input the actual port to overwrite it.

# Important Notes

## General

1. It is recommended to use a venv to keep your global python installation clean of the dependencies. After setting up the venv and activating it, you can install the requirements with the requirements.txt file (more about that in the "Usage" section)
2. The scanner does not need admin privilege to run
3. Make sure your folder structure matches the expected structure
4. Bluestacks settings must be the same as in pictures above. THIS IS VERY IMPORTANT!
5. BE CAREFUL to always copy the .xlsx file from the RokTracker folder when it is created, because in the next capture, there is a chance for it to get overwritten (very low chance).
6. Chinese letters might not be shown properly in CMD, but they are visible in the final .xlsx file.
7. You can do whatever you want in your computer when tool is scanning. Only be warned that copying can result in wrong governor names if it coincides with the name copy of the script.
8. Game Language should be English. Anything else will cause trouble in detecting inactive governors. Change it only for scan, if yours is different and then switch back.

## Scan

1. In order to get only your kingdoms ranks, the character that is currently logged in game must be in HOME KINGDOM, else you will get all the players in your KvK including players from different kingdoms.
2. The view before running the program should be at the top of power rankings or at the top of kill points rankings for the `rok-scanner.py` or at the top of an alliance leader board of your choice or at top of the personal honor rank for the `alliance-scanner.py`. No move should be made in this window until scanning is done.
3. [Only for kingdom scan] Account must be lower in ranks than the amount of players you want to scan. e.g. Cannot scan top 100 when character's rank is 85. Use a farm account instead.
4. [Only for kingdom scan] Resume Scan option starts scanning the middle governor that is displayed in screen. The 4th in order. So before starting the tool make sure that you are in the correct view in bluestacks.
