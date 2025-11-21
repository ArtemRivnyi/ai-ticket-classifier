import requests
import os
import json
import time

# Live URL from user request
BASE_URL = "https://ai-ticket-classifier-production.up.railway.app"
# Hardcoded key from app.js (needs to match Railway env var)
API_KEY = "sk_ORulUQRLvLHAueF3Ht1gXj9gTsY7xme3QD-UeVrO8nY"

def check_health():
    print(f"Checking Health at {BASE_URL}/api/v1/health ...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return False

def check_classify():
    print(f"\nChecking Classification at {BASE_URL}/api/v1/classify ...")
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    payload = {
        "ticket": "My internet is down and I cannot connect to the VPN."
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/classify", 
            headers=headers, 
            json=payload, 
            timeout=15
        )
        duration = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {duration:.2f}s")
        
        if response.status_code == 200:
            print("✅ API Key is VALID. Backend is working.")
            print(json.dumps(response.json(), indent=2))
            return True
        elif response.status_code == 401:
            print("❌ API Key is INVALID (401 Unauthorized).")
            print("Action Required: Update MASTER_API_KEY in Railway variables.")
            return False
        else:
            print(f"❌ Unexpected Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return False

if __name__ == "__main__":
    print("=== LIVE PRODUCTION VERIFICATION ===")
    health_ok = check_health()
    if health_ok:
        check_classify()
    else:
        print("\n⚠️ Health check failed. Skipping classification check.")
