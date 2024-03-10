@echo off
set NAME=EasyWallpaperInfo
set VENV_PATH=.venv
set ACTIVATE_PATH=%VENV_PATH%\Scripts\activate

IF NOT EXIST %ACTIVATE_PATH% (
    echo Creating virtual environment...
    virtualenv %VENV_PATH%
)

echo Activating virtual environment...
call %ACTIVATE_PATH%

echo Checking the requirements...
pip freeze | findstr /r /g:requirements.txt > nul
if %errorlevel% neq 0 (
    echo Installing missing or outdated requirements...
    pip install -r requirements.txt --upgrade --quiet
)

echo Starting %NAME%...
start /B "" "%VENV_PATH%/Scripts/pythonw.exe" EasyWallpaperInfo.pyw
