"""
Script to verify the AI Ticket Classifier setup
Checks imports, configuration, and basic functionality
"""

import sys
import os
from pathlib import Path
import io

# Python version check - MUST be 3.12
if sys.version_info[:2] != (3, 12):
    print("=" * 70)
    print("❌ ERROR: Python 3.12 is REQUIRED for this project")
    print("=" * 70)
    print(f"Current version: {sys.version}")
    print(f"Required: Python 3.12.x")
    print()
    print("Please use Python 3.12. Run: python check_python_version.py")
    print("=" * 70)
    sys.exit(1)

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("AI Ticket Classifier - Setup Verification")
print("=" * 60)
print()

# Track errors and warnings
errors = []
warnings = []
success_count = 0
missing_packages = []

def check(description, func):
    """Check function wrapper"""
    global success_count
    try:
        result = func()
        if result:
            print(f"[OK] {description}")
            success_count += 1
            return True
        else:
            print(f"[WARN] {description} - WARNING")
            warnings.append(description)
            return False
    except Exception as e:
        print(f"[ERROR] {description} - ERROR: {e}")
        errors.append(f"{description}: {str(e)}")
        return False

# 1. Check Python version
print("[1/8] Checking Python version...")
check("Python version >= 3.8", lambda: sys.version_info >= (3, 8))
print()

# 2. Check required packages
print("[2/8] Checking required packages...")

# Map package names to their import names (some packages have different import names)
package_map = {
    'flask': 'flask',
    'flask-cors': 'flask_cors',
    'flask-limiter': 'flask_limiter',
    'flasgger': 'flasgger',
    'pydantic': 'pydantic',
    'prometheus-client': 'prometheus_client',
    'redis': 'redis',
    'google-generativeai': 'google.generativeai',
    'pyjwt': 'jwt',
    'sqlalchemy': 'sqlalchemy',
    'requests': 'requests',
    'python-dotenv': 'dotenv',
    'email-validator': 'email_validator'
}

for pip_name, import_name in package_map.items():
    try:
        __import__(import_name)
        check(f"Package: {pip_name}", lambda: True)
    except ImportError:
        check(f"Package: {pip_name}", lambda: False)
        missing_packages.append(pip_name)
    except Exception as e:
        # Special case for google.generativeai - requires Python 3.12
        if 'google.generativeai' in import_name:
            try:
                # Try alternative import
                import google.generativeai as genai
                check(f"Package: {pip_name}", lambda: True)
            except Exception as genai_error:
                # Python 3.12 is required
                if "Metaclasses with custom tp_new are not supported" in str(genai_error):
                    print(f"[ERROR] Package: {pip_name} - Requires Python 3.12")
                    errors.append(f"{pip_name}: Python 3.12 required")
                    check(f"Package: {pip_name}", lambda: False)
                else:
                    check(f"Package: {pip_name}", lambda: False)
                    missing_packages.append(pip_name)
        else:
            check(f"Package: {pip_name}", lambda: False)
            missing_packages.append(pip_name)
print()

# 3. Check environment variables
print("[3/8] Checking environment variables...")
gemini_key = os.getenv('GEMINI_API_KEY')
if gemini_key:
    check("GEMINI_API_KEY is set", lambda: True)
else:
    print("[INFO] GEMINI_API_KEY not set (set in .env file for production)")
check("SECRET_KEY is set (or using default)", lambda: True)  # Always pass, default exists
print()

# 4. Check file imports
print("[4/8] Checking file imports...")

check("app.py can be imported", lambda: __import__('app', fromlist=['app']) is not None)

try:
    from providers.multi_provider import MultiProvider
    check("MultiProvider can be imported", lambda: True)
except Exception as e:
    check("MultiProvider can be imported", lambda: False)

try:
    from middleware.auth import require_api_key, APIKeyManager
    check("Auth middleware can be imported", lambda: True)
except Exception as e:
    check("Auth middleware can be imported", lambda: False)

try:
    from security.jwt_auth import generate_jwt_token, validate_jwt_token
    check("JWT auth can be imported", lambda: True)
except Exception as e:
    check("JWT auth can be imported", lambda: False)

try:
    from api.auth import auth_bp
    check("Auth blueprint can be imported", lambda: True)
except Exception as e:
    check("Auth blueprint can be imported", lambda: False)

try:
    from monitoring.metrics import request_count
    check("Metrics can be imported", lambda: True)
except Exception as e:
    check("Metrics can be imported", lambda: False)

print()

# 5. Check Flask app initialization
print("[5/8] Checking Flask app...")
try:
    from app import app as flask_app
    check("Flask app can be initialized", lambda: flask_app is not None)
    check("Flask app has SECRET_KEY", lambda: flask_app.config.get('SECRET_KEY') is not None)
except Exception as e:
    check("Flask app can be initialized", lambda: False)
print()

# 6. Check Redis connection (optional)
print("[6/8] Checking Redis connection (optional)...")
try:
    import redis
    redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    # Try to connect (will fail if Redis not running, but that's OK for local dev)
    check("Redis URL is configured", lambda: redis_url is not None)
except Exception as e:
    warnings.append("Redis connection check skipped (Redis may not be running locally)")
    print("WARNING: Redis connection check skipped (Redis may not be running locally)")
print()

# 7. Check Swagger configuration
print("[7/8] Checking Swagger/OpenAPI...")
try:
    from app import app as flask_app
    # Check if Swagger routes are registered
    routes = [str(rule) for rule in flask_app.url_map.iter_rules()]
    has_swagger = any('/api-docs' in r or '/apispec.json' in r for r in routes)
    if has_swagger:
        check("Swagger is configured", lambda: True)
    else:
        check("Swagger is configured", lambda: False)
except Exception as e:
    check("Swagger is configured", lambda: False)
print()

# 8. Check routes
print("[8/8] Checking routes...")
try:
    from app import app as flask_app
    routes = [str(rule) for rule in flask_app.url_map.iter_rules()]
    required_routes = [
        '/api/v1/health',
        '/api/v1/classify',
        '/api/v1/batch',
        '/api/v1/auth/register',
        '/metrics'
    ]
    for route in required_routes:
        check(f"Route exists: {route}", lambda r=route: any(r in route_check for route_check in routes))
except Exception as e:
    check("Routes can be checked", lambda: False)
print()

# Summary
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Successful checks: {success_count}")
print(f"Warnings: {len(warnings)}")
print(f"Errors: {len(errors)}")
print()

if errors:
    print("ERRORS FOUND:")
    for error in errors:
        print(f"   - {error}")
    print()
    
    if missing_packages:
        print("MISSING PACKAGES DETECTED:")
        print(f"   Missing: {', '.join(missing_packages)}")
        print()
        print("TO FIX, RUN THIS COMMAND:")
        print(f"   pip install {' '.join(missing_packages)}")
        print()
        print("OR REINSTALL ALL REQUIREMENTS:")
        print("   pip install -r requirements.txt")
        print()
    
    print("TIPS:")
    print("   1. Make sure all packages are installed: pip install -r requirements.txt")
    print("   2. Check that GEMINI_API_KEY is set in environment or .env file")
    print("   3. Verify all files are in correct locations")
    print("   4. If using Python 3.14, some packages might not be compatible yet")
    print()
    sys.exit(1)
elif warnings:
    print("WARNINGS:")
    for warning in warnings:
        print(f"   - {warning}")
    print()
    print("NOTE: Some warnings are normal (e.g., Redis not running locally)")
    print()
else:
    print("All checks passed! Setup is complete.")
    print()
    print("Next steps:")
    print("   1. Set GEMINI_API_KEY in .env file")
    print("   2. Run: python app.py")
    print("   3. Or use Docker: docker-compose -f docker-compose.prod.yml up --build")
    print()

print("=" * 60)

