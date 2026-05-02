import requests
import json

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2YTJhZmIzYi00MzMzLTQwZDUtOGE0Zi1jNjc4N2E3OTBlMGEiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiMTlkYjU0ZDktOTk5ZS00ZDY1LWE2YTUtNGU2NDY1YWQyMGI5IiwiaWF0IjoxNzc2ODk4MjkyLCJleHAiOjE3Nzk0MDgwMDB9.h1wDPxLr7wGMf2wvISxl-FkX9NhkTSnqfXaPZYC3IA8"
N8N_URL = "http://localhost:5678/api/v1"
HEADERS = {"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"}

with open("n8n/industrial_distribution_loop.json") as f:
    wf = json.load(f)

print("Updating workflow 2...")
resp = requests.put(f"{N8N_URL}/workflows/2", headers=HEADERS, json=wf)
if resp.status_code == 200:
    print("Success")
    print("Activating...")
    r2 = requests.post(f"{N8N_URL}/workflows/2/activate", headers=HEADERS)
    if r2.status_code == 200:
        print("Successfully activated!")
    else:
        print(f"Failed to activate: {r2.text}")
else:
    print(f"Failed: {resp.text}")
