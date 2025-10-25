import requests
import json

def test_classify_endpoint():
    test_cases = [
        {"ticket": "I can't connect to Wi-Fi", "priority": "high"},
        {"ticket": "My account is locked", "priority": "high"},  # ✅ ИСПРАВЛЕНО
        {"ticket": "I need a refund for my subscription", "priority": "medium"}
    ]
    
    for i, test_case in enumerate(test_cases):
        try:
            response = requests.post(
                "http://127.0.0.1:5000/api/v1/classify",  # ✅ ИСПРАВЛЕН URL
                json=test_case,
                timeout=10
            )
            
            print(f"\n--- Test {i+1} ---")
            print(f"Request: {test_case}")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Category: {data.get('category')}")
                print(f"Priority: {data.get('priority')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_classify_endpoint()