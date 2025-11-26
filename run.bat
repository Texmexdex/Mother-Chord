@echo off
echo [TeX's Mother-Chord] Launching...

if not exist "venv" (
    echo [ERROR] Virtual environment not found. Run setup.bat first.
    pause
    exit /b
)

call venv\Scripts\activate
python main.py

if %errorlevel% neq 0 (
    echo [ERROR] Application crashed.
    pause
)
