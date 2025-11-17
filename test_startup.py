"""
Quick test to verify app can start with current environment
"""

import os
import sys
import io
from dotenv import load_dotenv

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load environment variables
load_dotenv()

print("=" * 60)
print("Testing App Startup")
print("=" * 60)
print()

# Check environment variables
print("Environment Variables:")
print(f"  GEMINI_API_KEY: {'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")
print(f"  MASTER_API_KEY: {'SET' if os.getenv('MASTER_API_KEY') else 'NOT SET'}")
print(f"  FLASK_ENV: {os.getenv('FLASK_ENV', 'development')}")
print(f"  REDIS_URL: {os.getenv('REDIS_URL', 'NOT SET')}")
print()

# Try to import app
print("Testing imports...")
try:
    from app import app as flask_app
    print("[OK] Flask app imported successfully")
    
    # Check routes
    routes = [str(rule) for rule in flask_app.url_map.iter_rules()]
    print(f"[OK] Found {len(routes)} routes")
    
    # Check key routes
    key_routes = [
        '/api/v1/health',
        '/api/v1/classify',
        '/api/v1/batch',
        '/metrics'
    ]
    for route in key_routes:
        if any(route in r for r in routes):
            print(f"  [OK] {route}")
        else:
            print(f"  [ERROR] {route} - MISSING")
    
    print()
    print("=" * 60)
    print("[OK] App is ready to start!")
    print("=" * 60)
    print()
    print("To start the app, run:")
    print("  python app.py")
    print()
    print("Or in production mode:")
    print("  gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app")
    print()
    
except Exception as e:
    print(f"[ERROR] Error importing app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

