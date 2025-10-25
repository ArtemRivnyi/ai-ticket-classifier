# test_config.py
import sys
import os

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from classify import classify_ticket
    print("✅ classify.py imports successfully")
    
    # Check environment variables loading
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("✅ GEMINI_API_KEY loaded")
    else:
        print("❌ GEMINI_API_KEY not found")
        
except Exception as e:
    print(f"❌ Import error: {e}")