@echo off
REM Windows batch script to verify setup

echo ============================================================
echo AI Ticket Classifier - Setup Verification
echo ============================================================
echo.

echo [1/4] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)
echo.

echo [2/4] Checking required packages...
python -c "import flask; import flask_cors; import flask_limiter; import flasgger; print('All core packages installed')"
if %errorlevel% neq 0 (
    echo ERROR: Some packages are missing. Run: pip install -r requirements.txt
    exit /b 1
)
echo.

echo [3/4] Running setup verification script...
python check_setup.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Setup verification failed. Check output above.
    exit /b 1
)
echo.

echo [4/4] Testing Flask app import...
python -c "from app import app; print('Flask app imported successfully')"
if %errorlevel% neq 0 (
    echo ERROR: Cannot import Flask app. Check errors above.
    exit /b 1
)
echo.

echo ============================================================
echo Setup verification complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Create .env file with GEMINI_API_KEY
echo 2. Run: python app.py
echo.

pause

