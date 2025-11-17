# Python Version Requirements

## Required Version

**This project requires Python 3.12**

## Why Python 3.12?

1. **Compatibility**: Python 3.12 is the latest stable version with full support for all dependencies
2. **Google Gemini**: The `google-generativeai` package has known compatibility issues with Python 3.14+ due to metaclass implementation changes
3. **Test Coverage**: All tests are designed and verified to pass on Python 3.12
4. **Production Stability**: Python 3.12 provides the best balance of features and stability

## Installation

### Using pyenv (Recommended)

```bash
# Install Python 3.12
pyenv install 3.12.0

# Set local version
pyenv local 3.12.0

# Verify
python --version  # Should show Python 3.12.x
```

### Using Official Installer

Download and install Python 3.12 from [python.org](https://www.python.org/downloads/)

### Using Virtual Environment

```bash
# Create virtual environment with Python 3.12
python3.12 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Verify
python --version  # Should show Python 3.12.x
```

## Docker

The Dockerfile is already configured to use Python 3.12:

```dockerfile
FROM python:3.12-slim
```

## CI/CD

GitHub Actions workflows are configured to use Python 3.12:

```yaml
python-version: '3.12'
```

## Verification

Check your Python version:

```bash
python --version
# Should output: Python 3.12.x
```

Run the production checklist:

```bash
python production_checklist.py
```

## Troubleshooting

If you see errors related to `google-generativeai` or metaclass issues, ensure you're using Python 3.12:

```bash
# Check version
python --version

# If not 3.12, recreate virtual environment
python3.12 -m venv venv312
source venv312/bin/activate  # or venv312\Scripts\activate on Windows
pip install -r requirements.txt
```

