@echo off
echo [SYNTH BRIDGE] Setup...

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.10+.
    pause
    exit /b
)

:: Create venv
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

:: Activate & install
call venv\Scripts\activate

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

echo [INFO] Installing dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Installation failed.
    pause
    exit /b
)

echo.
echo [SUCCESS] Setup complete! Run 'run.bat' to start.
pause
