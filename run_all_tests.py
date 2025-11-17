"""
Comprehensive test runner for AI Ticket Classifier
Runs all tests with coverage and generates report
"""
import sys
import subprocess
import os
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print colored header"""
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    """Print warning message"""
    try:
        print(f"{YELLOW}WARNING: {text}{RESET}")
    except UnicodeEncodeError:
        print(f"WARNING: {text}")

def run_command(cmd, description):
    """Run a command and return success status"""
    print_header(description)
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print_warning(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {e}")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    """Run all tests"""
    print_header("AI Ticket Classifier - Full Test Suite")
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print_error("pytest is not installed!")
        print("Install with: pip install pytest pytest-cov pytest-mock")
        sys.exit(1)
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    results = {}
    
    # 1. Check setup
    print_header("Step 1: Environment Check")
    cmd = f"{sys.executable} check_setup.py"
    results['setup'] = run_command(cmd, "Running environment check")
    
    # 2. Run pytest unit tests
    print_header("Step 2: Unit Tests (pytest)")
    cmd = "pytest tests/ test_app.py -v --tb=short"
    results['pytest'] = run_command(cmd, "Running pytest unit tests")
    
    # 3. Run pytest with coverage
    print_header("Step 3: Test Coverage")
    cmd = "pytest tests/ test_app.py --cov=app --cov=middleware --cov=providers --cov=api --cov=security --cov-report=term-missing --cov-report=html"
    results['coverage'] = run_command(cmd, "Running tests with coverage")
    
    # 4. Production checklist
    print_header("Step 4: Production Checklist")
    cmd = "python production_checklist.py"
    results['checklist'] = run_command(cmd, "Running production checklist")
    
    # 5. Syntax check
    print_header("Step 5: Syntax Check")
    python_files = [
        "app.py",
        "api/auth.py",
        "middleware/auth.py",
        "providers/multi_provider.py",
        "providers/gemini_provider.py",
        "security/jwt_auth.py"
    ]
    syntax_ok = True
    for file in python_files:
        if Path(file).exists():
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", file],
                capture_output=True
            )
            if result.returncode == 0:
                print_success(f"{file} - OK")
            else:
                print_error(f"{file} - Syntax error")
                print(result.stderr.decode())
                syntax_ok = False
    results['syntax'] = syntax_ok
    
    # Summary
    print_header("Test Summary")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for name, status in results.items():
        if status:
            print_success(f"{name}")
        else:
            print_error(f"{name}")
    
    print(f"\n{BLUE}Results: {passed}/{total} checks passed{RESET}\n")
    
    if passed == total:
        print_success("All tests passed! ✅")
        return 0
    else:
        print_error(f"{total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

