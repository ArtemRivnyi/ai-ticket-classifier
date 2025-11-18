#!/usr/bin/env python3
"""
Check Python version - MUST be 3.12.x
"""
import sys

def check_python_version():
    """Verify Python version is 3.12.x"""
    if sys.version_info[:2] != (3, 12):
        print("=" * 70)
        print("❌ ERROR: Python 3.12 is REQUIRED for this project")
        print("=" * 70)
        print(f"Current version: {sys.version}")
        print(f"Required: Python 3.12.x")
        print()
        print("Please install Python 3.12:")
        print("  Windows: https://www.python.org/downloads/release/python-3120/")
        print("  Or use: pyenv install 3.12.0")
        print()
        print("Then create a virtual environment:")
        print("  python3.12 -m venv venv")
        print("  venv\\Scripts\\activate  # Windows")
        print("  source venv/bin/activate  # Linux/Mac")
        print("=" * 70)
        sys.exit(1)
    
    print(f"✅ Python version OK: {sys.version}")
    return True

if __name__ == "__main__":
    check_python_version()

