import requests

url = "http://127.0.0.1:8055/auth/register"
headers = {"Content-Type": "application/json", "X-Security-Key": "dre_secure_2026"}
data = {"username": "Dre", "consent_given": True}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
