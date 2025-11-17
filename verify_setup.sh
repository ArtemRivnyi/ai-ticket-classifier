#!/bin/bash
# Linux/Mac shell script to verify setup

echo "============================================================"
echo "AI Ticket Classifier - Setup Verification"
echo "============================================================"
echo ""

echo "[1/4] Checking Python installation..."
python3 --version || python --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python is not installed or not in PATH"
    exit 1
fi
echo ""

echo "[2/4] Checking required packages..."
python3 -c "import flask; import flask_cors; import flask_limiter; import flasgger; print('All core packages installed')" || python -c "import flask; import flask_cors; import flask_limiter; import flasgger; print('All core packages installed')"
if [ $? -ne 0 ]; then
    echo "ERROR: Some packages are missing. Run: pip install -r requirements.txt"
    exit 1
fi
echo ""

echo "[3/4] Running setup verification script..."
python3 check_setup.py || python check_setup.py
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Setup verification failed. Check output above."
    exit 1
fi
echo ""

echo "[4/4] Testing Flask app import..."
python3 -c "from app import app; print('Flask app imported successfully')" || python -c "from app import app; print('Flask app imported successfully')"
if [ $? -ne 0 ]; then
    echo "ERROR: Cannot import Flask app. Check errors above."
    exit 1
fi
echo ""

echo "============================================================"
echo "Setup verification complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Create .env file with GEMINI_API_KEY"
echo "2. Run: python app.py"
echo ""

