import requests
import json
import os

N8N_URL = "http://localhost:5678/api/v1"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2YTJhZmIzYi00MzMzLTQwZDUtOGE0Zi1jNjc4N2E3OTBlMGEiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiMTlkYjU0ZDktOTk5ZS00ZDY1LWE2YTUtNGU2NDY1YWQyMGI5IiwiaWF0IjoxNzc2ODk4MjkyLCJleHAiOjE3Nzk0MDgwMDB9.h1wDPxLr7wGMf2wvISxl-FkX9NhkTSnqfXaPZYC3IA8"

headers = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

print("Fetching workflows...")
response = requests.get(f"{N8N_URL}/workflows", headers=headers)

if response.status_code == 200:
    workflows = response.json().get("data", [])
    print(f"Found {len(workflows)} workflows.")
    
    for wf in workflows:
        print(f"Activating workflow: {wf['name']} (ID: {wf['id']})")
        # To activate, we need to activate the workflow
        activate_url = f"{N8N_URL}/workflows/{wf['id']}/activate"
        act_resp = requests.post(activate_url, headers=headers)
        if act_resp.status_code == 200:
            print(" -> Successfully activated.")
        else:
            print(f" -> Failed to activate: {act_resp.status_code} {act_resp.text}")
else:
    print(f"Failed to fetch workflows: {response.status_code} {response.text}")
