@echo off
REM Setup script for Multi-Annotator Dataset Conflict Detection System (Windows)

echo Setting up Multi-Annotator Conflict Detection Environment...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or later.
    exit /b 1
)

echo Python version:
python --version

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Setup complete!
echo.
echo To activate the environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To run the conflict detector, run:
echo   python conflict_detector.py
echo.
echo To run tests, run:
echo   python -m pytest test_conflict_detector.py -v
