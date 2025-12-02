@echo off
cd /d "d:\Downloads\1\Claude-haiku-4.5\v-lkan_25_12_2"
echo Creating virtual environment...
"D:\package\venv310\Scripts\python.exe" -m venv venv_conflict
echo.
echo Activating virtual environment...
call venv_conflict\Scripts\activate.bat
echo.
echo Installing dependencies...
pip install -q -r requirements.txt
echo.
echo Running analysis...
python run_analysis.py
echo.
echo Running tests...
python -m pytest test_conflict_detector.py -v --tb=short
pause
