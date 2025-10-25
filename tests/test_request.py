import requests

try:
    response = requests.post(
        "http://127.0.0.1:5000/api/v1/classify",  # ✅ FIXED URL
        json={"ticket": "I can't connect to Wi-Fi on my laptop"},
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Content: {response.text}")
    
    if response.status_code == 200:
        print(f"JSON: {response.json()}")
    else:
        print("Server returned non-200 status code")
        
except requests.exceptions.JSONDecodeError as e:
    print(f"JSON Decode Error: {e}")
    print(f"Response text was: {response.text}")
except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: {e}")
    print("Make sure the Flask server is running on port 5000")
except Exception as e:
    print(f"Unexpected error: {e}")