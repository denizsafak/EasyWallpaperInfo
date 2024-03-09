@echo off
IF NOT EXIST .env\Scripts\activate (
    echo Creating virtual environment...
    virtualenv .env
    echo Virtual environment created.
)

echo Activating virtual environment...
call .env\Scripts\activate

echo Installing requirements...
pip install -r requirements.txt

echo Starting EasyWallpaperInfo.pyw...
start /B "" ".env/Scripts/pythonw.exe" EasyWallpaperInfo.pyw