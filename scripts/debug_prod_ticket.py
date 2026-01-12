import requests
import json

BASE_URL = "https://ai-ticket-classifier-production.up.railway.app"
API_KEY = "sk_ORulUQRLvLHAueF3Ht1gXj9gTsY7xme3QD-UeVrO8nY"

tickets = [
    "The API is returning 500 Internal Server Error for all requests.",
    "The system is very slow today, pages take forever to load.",
    "Is there a way to integrate this with Slack?",
]

print(f"Debugging tickets against {BASE_URL}...\n")

for ticket in tickets:
    print(f"Ticket: {ticket}")
    headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}
    payload = {"ticket": ticket}

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/classify", headers=headers, json=payload, timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)
