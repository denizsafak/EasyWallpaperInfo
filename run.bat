@echo off
setlocal enabledelayedexpansion
set NAME=EasyWallpaperInfo
set RUN=EasyWallpaperInfo.pyw
set "requirementsFile=requirements.txt"
set VENV_PATH=.venv
set ACTIVATE_PATH=%VENV_PATH%\Scripts\activate

:: Check if Python is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed.
    set /p "userinp=Do you want to install Python (y/n)? "
    if /i "!userinp!"=="y" (
        echo Opening download link...
        start https://www.python.org/downloads/
        exit /b
    ) else (
        echo Please install Python and try again.
        pause
        exit /b
    )
)

:: Check if virtual environment exists
IF NOT EXIST %ACTIVATE_PATH% (
    echo Creating virtual environment...
    python -m venv %VENV_PATH%
) ELSE (
    goto check_python
)

:: Check if Python exists at the path stored in the virtual environment
:check_python
%VENV_PATH%\Scripts\python.exe --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found at the path stored in the virtual environment.
    echo Recreating virtual environment...
    rmdir /s /q %VENV_PATH%
    python -m venv %VENV_PATH%
)

echo Activating virtual environment...
call %ACTIVATE_PATH%

echo Checking the requirements...
for /f "delims=" %%i in (%requirementsFile%) do (
    pip freeze | findstr /c:%%i > nul
    if errorlevel 1 (
        echo Installing package: %%i
        pip install %%i --upgrade --quiet
    )
)

echo Starting %NAME%...
start /B "" "%VENV_PATH%/Scripts/pythonw.exe" %RUN%