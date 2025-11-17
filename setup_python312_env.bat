@echo off
echo ========================================
echo Setting up Python 3.12 environment
echo ========================================
echo.

echo [1] Creating virtual environment with Python 3.12...
py -3.12 -m venv venv312

echo.
echo [2] Activating virtual environment...
call venv312\Scripts\activate.bat

echo.
echo [3] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [4] Installing dependencies...
pip install -r requirements.txt

echo.
echo [5] Verifying Python version...
python --version

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo To activate the environment in the future, run:
echo   venv312\Scripts\activate
echo.
echo Or use Git Bash:
echo   source venv312/Scripts/activate
echo.

