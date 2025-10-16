import requests

response = requests.post(
    "http://127.0.0.1:5000/classify",
    json={"ticket": "I can’t connect to Wi-Fi on my laptop"}
)

print(response.json())
