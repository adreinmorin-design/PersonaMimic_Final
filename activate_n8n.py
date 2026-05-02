import requests

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2YTJhZmIzYi00MzMzLTQwZDUtOGE0Zi1jNjc4N2E3OTBlMGEiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiMTlkYjU0ZDktOTk5ZS00ZDY1LWE2YTUtNGU2NDY1YWQyMGI5IiwiaWF0IjoxNzc2ODk4MjkyLCJleHAiOjE3Nzk0MDgwMDB9.h1wDPxLr7wGMf2wvISxl-FkX9NhkTSnqfXaPZYC3IA8"
N8N_URL = "http://localhost:5678/api/v1"
HEADERS = {"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"}

print("Fetching workflows to activate...")
resp = requests.get(f"{N8N_URL}/workflows", headers=HEADERS)
if resp.status_code == 200:
    for wf in resp.json().get("data", []):
        wid = wf['id']
        print(f"Activating {wf['name']} ({wid})...")
        r = requests.post(f"{N8N_URL}/workflows/{wid}/activate", headers=HEADERS)
        if r.status_code == 200:
            print(" -> Success")
        else:
            print(f" -> Failed: {r.text}")
else:
    print(f"Failed to fetch workflows: {resp.text}")
