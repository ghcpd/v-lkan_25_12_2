@echo off
REM Setup script for Multi-Annotator Conflict Detection System (Windows)

echo ==========================================
echo Multi-Annotator Conflict Detection Setup
echo ==========================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.9 or higher.
    exit /b 1
)

python --version

REM Create virtual environment
echo.
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    echo Virtual environment created successfully.
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies...
if exist requirements.txt (
    pip install -r requirements.txt
    echo Dependencies installed successfully.
) else (
    echo Error: requirements.txt not found.
    exit /b 1
)

REM Create output directories
echo.
echo Creating output directories...
if not exist output mkdir output
if not exist reports mkdir reports
echo Directories created.

REM Run tests to verify installation
echo.
echo Running tests to verify installation...
python -m pytest test_conflict_detector.py -v

if errorlevel 1 (
    echo.
    echo Warning: Some tests failed. Please check the output above.
    exit /b 1
)

echo.
echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo To get started:
echo   1. Activate the virtual environment: venv\Scripts\activate.bat
echo   2. Run the application: python main.py --help
echo   3. Process your dataset: python main.py --input tickets_label.jsonl --output output\results.jsonl
echo.

pause
