#!/usr/bin/env python3
"""
Quick coverage check script
"""
import subprocess
import sys

def main():
    print("=" * 60)
    print("Running tests with coverage...")
    print("=" * 60)
    
    # Run pytest with coverage
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", 
         "--cov=app", "--cov-report=term-missing", "-q"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    # Extract coverage for app.py
    lines = result.stdout.split('\n')
    for line in lines:
        if 'app.py' in line or 'TOTAL' in line:
            print(line)
    
    print("\n" + "=" * 60)
    print("Coverage check complete!")
    print("=" * 60)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())

