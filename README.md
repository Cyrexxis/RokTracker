# RokTracker

**Now with version 2 faster than ever, around 15 seconds per governor! Because it's a pre-release only the core rok-tracker.py works, the alliance scanner will be updated at a later time.**

> [!IMPORTANT]  
> Due to major changes on the library side of this project you need to reread the requirements and also the newly added installation section before being able to run the new version if you upgrade form the old one.

Open Source Rise of Kingdoms Stats Management Tool. Track TOP X Players in kingdom / alliance / honor leaderboard. Depending on what you scan the resulting .xlsx will look different:

For kingdom rankings Governor Id, Governor Name, Power, Kill Points, Ranged Points, T1/T2/T3/T4/T5 Kills, Total kills, T4+T5 kills, Dead troops, RSS Gathered, RSS Assistance, Helps and Alliance name will get saved.

For the honor and alliance rankings only the governor name and the score will be saved. Because there is no guarantee that the name is correct a picture of the name will be saved in addition.

This is a heavily modified version of the original tool from [nikolakis1919](https://github.com/nikolakis1919) in the repository [https://github.com/nikolakis1919/RokTracker](https://github.com/nikolakis1919/RokTracker)

# Required

1. Bluestacks 5 Installation [https://www.bluestacks.com/de/bluestacks-5.html](https://www.bluestacks.com/de/bluestacks-5.html)
2. Python 3.11.0 Installation [https://www.python.org/downloads/release/python-3110/](https://www.python.org/downloads/release/python-3110/)
3. On Windows you need to download the tesserocr manualy to install it with pip [https://github.com/simonflueckiger/tesserocr-windows_build/releases](https://github.com/simonflueckiger/tesserocr-windows_build/releases)
4. To use tesserocr you also need to download the trained tesseract models [https://github.com/tesseract-ocr/tessdata](https://github.com/tesseract-ocr/tessdata)
5. Adb Platform Tools Download and Extract(See Important Notes) [https://dl.google.com/android/repository/platform-tools_r31.0.3-windows.zip](https://dl.google.com/android/repository/platform-tools_r31.0.3-windows.zip)
6. On Windows "Microsoft Build Tools für C++" might be required for some of the python packages [https://visualstudio.microsoft.com/de/visual-cpp-build-tools/](https://visualstudio.microsoft.com/de/visual-cpp-build-tools/)
7. Windows 10-Tested, Windows 7 or Windows 11 could be fine.

# Installation

To use this tool a little bit of command line knowledge is required (you need to be able to open your powershell in the downloaded or cloned folder). Apart from that the installation and usage of this tool is pretty easy.

1. Download and install Bluestacks + Python + Build Tools for C++
2. Download tesserocr wheel and tessdata and put them in the deps folder
3. Extract the tessdata zip to a tessdata-main folder inside deps
4. Download adb platform tools and extract them into a platform-tools folder in the main directory of this scanner
5. Open your terminal in this folder and create a venv via `python -m venv venv`
6. Activate that venv via `./venv/Scrips/activate`
7. Install the python requirements via `pip install -r requirements.txt`
8. Install tesserocr via `pip install ./deps/[your downloaded wheel]`
9. You are done, congrats ;)

# Features

`rok-tracker.py`:

- complete kingdom ranking sca
- detection for wrong kills based on if kills to kill points are correct
  - in case something doesn't check out the corresponding images are saved in the `manual_review`-folder (prefix F) and a warning is logged in the log file.
- option to try to recover kills if wrong kills are detected
  - nevertheless the same images as for a fail get copied to the `manual_review`-folder (prefix R) and a info is logged in the log file.
- detection of inactive accounts
  - an inactive account is an account that cannot be clicked in the kingdom rankings
  - those are skipped automatically and it is optionally possible to save a screenshot of the name in the `inactives`-folder.

`alliance-scanner.py`:

- complete alliance ranking scan
- complete personal honor ranking scan
- due to how the game works the names are very inaccurate and it is not possible to track the governor id

# Bluestacks 5 Settings

![Bluestacks Performance Settings](images/bluestacks-performance.png)
![Bluestacks Display Settings](images/bluestacks-display.png)
![Bluestacks Advanced Settings](images/bluestacks-advanced.png)

Everything (maybe not the performance, adjust that to your PC) should be like this. The scanner script tries to find the current debugging port by reading the bluestacks config. For that to work the emulator used for scanning should have the instance name "RoK Tracker" and you need to change the config location in the scanner.py file to match your Bluestacks installation. If the auto detect fails it will default to 5555 and you can input the actual port to overwrite it.

# Important Notes

1. It is recommended to use a venv to keep your global python installation clean of the dependencies. After setting up the venv and activating it, you can install the requirements with the requirements.txt file (more about that in the "Usage"" section)

2. You must run the .ps1 file without administration privileges.

3. Make sure the tesseract executable is on the PATH variable of your machine

4. Platform tools folder should be extracted as a folder inside the Tracker's folder. Like the following image

   ![](images/platform-tools-pos.png)

5. In order to get only your kingdoms ranks, the character that is currently logged in game must be in HOME KINGDOM, else you will get all the players in your KvK including players from different kingdoms.

6. Game Language should be English. Anything else will cause trouble in detecting inactive governors. Change it only for scan, if yours is different and then switch back.

7. The view before running the programme should be at the top of power rankings or at the top of kill points rankings for the `rok-scanner.py` or at the top of an alliance leader board of your choice or at top of the personal honor rank for the `alliance-scanner.py`. No move should be made in this window until scanning is done.

8. [Only for kingdom scan] Account must be lower in ranks than the amount of players you want to scan. e.g. Cannot scan top 100 when character's rank is 85. Use a farm account instead.

9. You can see tool's progress in CMD when it's running.

10. Chinese letters might not be shown properly in CMD but they are visible in the final .xlsx file.

11. Bluestacks settings must be the same as in pictures above. THIS IS VERY IMPORTANT!

12. You can do whatever you want in your computer when tool is scanning. Only be warned that copying can result in wrong governor names if it coincides with the name copy of the script.

13. [Only for kingdom scan] Resume Scan option starts scanning the middle governor that is displayed in screen. The 4th in order. So before starting the tool make sure that you are in the correct view in bluestacks.

14. BE CAREFUL to always copy the .xlsx file from the RokTracker folder when it is created, because in the next capture, there is a chance to overwrite.

# Usage

These scripts runs completely in the command line. When you run them, they will ask all the important inputs and then start scanning until they reach either the target amount of persons or they reach the end of the leaderboard. You can always stop the scan by pressing CRTL+C and confirming. (But it might happen that doing so will case tesseract to go on a rampage, to be sure be prepared to kill the python process in another command line window)

## Kingdom scan

There are two ways of starting the script. First option is to simply run the powershell script. That script automatically creates and loads a venv in the venv folder, installs all dependencies and starts the actual scanner script (Make sure to have your python 3.11 selected as default version by checking the output of `python --version`):

```powershell
.\rok-scanner.ps1
```

The other way is to manually do all that:

```powershell
python -m venv ./venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python rok-scanner.py
```

Options on startup:

![](images/cmd-options.png)

Single result in cmd:

![](images/example-output.png)

Results in excel file.
![](images/excel-example.png)

## Alliance or Honor scan

Basically the same setup as the kingdom scan, but launch the other script:

```powershell
.\alliance-scanner.ps1
```

or

```powershell
python -m venv ./venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python alliance-scanner.py
```
