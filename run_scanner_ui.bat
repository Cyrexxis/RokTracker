@ECHO OFF
SET "scriptdir=%~dp0"
IF NOT "%scriptdir:~-1%"=="\" SET "scriptdir=%scriptdir%\"
ECHO Installation folder: %scriptdir%

IF NOT EXIST "%scriptdir%platform-tools\" (
  ECHO The platform-tools folder is missing. Please follow the installation process in the readme.
  ECHO It should be located at "%scriptdir%platform-tools\"
  PAUSE
  EXIT
)

IF NOT EXIST "%scriptdir%deps\" (
  ECHO The deps folder is missing. Please follow the installation process in the readme.
  ECHO It should be located at "%scriptdir%deps\"
  PAUSE
  EXIT
)

IF NOT EXIST "%scriptdir%deps\tessdata-main\" (
  ECHO The tessdata-main folder is missing in the deps folder. Please follow the installation process in the readme.
  ECHO It should be located at "%scriptdir%deps\tessdata-main\"
  PAUSE
  EXIT
)

powershell.exe -noLogo -ExecutionPolicy unrestricted -file %scriptdir%graphic_scanner.ps1