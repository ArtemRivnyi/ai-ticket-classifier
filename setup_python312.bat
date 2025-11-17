@echo off
REM Script to setup Python 3.12 environment for AI Ticket Classifier

echo ============================================================
echo Setting up Python 3.12 environment
echo ============================================================
echo.

REM Check if Python 3.12 is available
where py -3.12 >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python 3.12 not found!
    echo Please install Python 3.12 first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Checking Python 3.12...
py -3.12 --version
if %errorlevel% neq 0 (
    echo ERROR: Python 3.12 check failed
    pause
    exit /b 1
)
echo.

echo [2/4] Creating virtual environment...
if exist venv312 (
    echo Virtual environment already exists, removing...
    rmdir /s /q venv312
)

py -3.12 -m venv venv312
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo.

echo [3/4] Activating virtual environment...
call venv312\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

echo [4/4] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo ============================================================
echo Setup complete!
echo ============================================================
echo.
echo To activate the environment, run:
echo   venv312\Scripts\activate
echo.
echo To run the app:
echo   python app.py
echo.
echo To run production checklist:
echo   python production_checklist.py
echo.

pause

