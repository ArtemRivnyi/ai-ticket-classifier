#!/bin/bash
# Script to setup Python 3.12 environment for AI Ticket Classifier

echo "============================================================"
echo "Setting up Python 3.12 environment"
echo "============================================================"
echo ""

# Check if Python 3.12 is available
if ! command -v python3.12 &> /dev/null; then
    echo "ERROR: Python 3.12 not found!"
    echo "Please install Python 3.12 first."
    echo "Download from: https://www.python.org/downloads/"
    exit 1
fi

echo "[1/4] Checking Python 3.12..."
python3.12 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3.12 check failed"
    exit 1
fi
echo ""

echo "[2/4] Creating virtual environment..."
if [ -d "venv312" ]; then
    echo "Virtual environment already exists, removing..."
    rm -rf venv312
fi

python3.12 -m venv venv312
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi
echo ""

echo "[3/4] Activating virtual environment..."
source venv312/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi
echo ""

echo "[4/4] Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo ""

echo "============================================================"
echo "Setup complete!"
echo "============================================================"
echo ""
echo "To activate the environment, run:"
echo "  source venv312/bin/activate"
echo ""
echo "To run the app:"
echo "  python app.py"
echo ""
echo "To run production checklist:"
echo "  python production_checklist.py"
echo ""

