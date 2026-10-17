@echo off
rem Opens the RoughCut gallery. The first run sets up Python packages, which takes a minute.
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
    echo Setting up RoughCut for the first time. This takes a minute...
    py -3 -m venv .venv 2>nul || python -m venv .venv
    if errorlevel 1 (
        echo Could not create the Python environment. Is Python 3.14 installed?
        pause
        exit /b 1
    )
    ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
    if errorlevel 1 (
        echo Installing packages failed. Check the internet connection and try again.
        rmdir /s /q .venv
        pause
        exit /b 1
    )
)
start "" ".venv\Scripts\pythonw.exe" -m roughcut.gallery %*
