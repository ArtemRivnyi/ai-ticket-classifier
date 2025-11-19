import requests
import json
import os

BASE_URL = "http://localhost:5000/api/v1"
# Use a fake key for local testing if auth is disabled or mock it
# But wait, auth IS enabled. I need a valid key.
# I will use the generate_api_key script to make one first? 
# Or just bypass if I can? No, I should test with a key.
# Actually, for local testing I can just use the MASTER_API_KEY if set, or generate one.
# Let's assume I can generate one.

def test_endpoints():
    print("Testing endpoints...")
    
    # 1. Generate Key (simulated or manual)
    # For this test script, I'll assume I need to provide a key or run it where I can see the output
    # I'll skip auth for now and see if I get 401, which confirms auth is working at least.
    
    headers = {"Content-Type": "application/json"}
    
    # 2. Test Batch
    print("\nTesting /batch (Expect 401 without key)...")
    batch_payload = {
        "tickets": ["Ticket 1", "Ticket 2"]
    }
    try:
        resp = requests.post(f"{BASE_URL}/batch", json=batch_payload, headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

    # 3. Test Webhooks
    print("\nTesting /webhooks (Expect 401 without key)...")
    webhook_payload = {
        "url": "https://example.com/webhook"
    }
    try:
        resp = requests.post(f"{BASE_URL}/webhooks", json=webhook_payload, headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoints()
