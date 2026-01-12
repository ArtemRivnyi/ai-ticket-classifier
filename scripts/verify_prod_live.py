import requests
import json
import time

BASE_URL = "https://ai-ticket-classifier-production.up.railway.app/api/v1"
API_KEY = "sk_ORulUQRLvLHAueF3Ht1gXj9gTsY7xme3QD-UeVrO8nY"  # Demo key


def test_live_endpoints():
    print(f"Testing Live Endpoints at {BASE_URL}...")

    headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}

    # 1. Test Batch
    print("\n1. Testing /batch...")
    batch_payload = {
        "tickets": [
            "My internet is down and I cannot work.",
            "I need a license for PyCharm.",
            "The printer on the 2nd floor is jammed.",
        ]
    }
    try:
        resp = requests.post(f"{BASE_URL}/batch", json=batch_payload, headers=headers)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("Success! Response snippet:")
            print(json.dumps(resp.json(), indent=2)[:200] + "...")
        else:
            print(f"Failed. Response: {resp.text}")
    except Exception as e:
        print(f"Error testing batch: {e}")

    # 2. Test Webhooks
    print("\n2. Testing /webhooks...")
    webhook_payload = {
        "url": "https://webhook.site/00000000-0000-0000-0000-000000000000"  # Fake URL, just testing registration
    }
    try:
        resp = requests.post(
            f"{BASE_URL}/webhooks", json=webhook_payload, headers=headers
        )
        print(f"Status: {resp.status_code}")
        if resp.status_code == 201:
            print("Success! Response:")
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"Failed. Response: {resp.text}")
    except Exception as e:
        print(f"Error testing webhooks: {e}")


if __name__ == "__main__":
    test_live_endpoints()
