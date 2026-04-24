import requests
import json
import time

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2YTJhZmIzYi00MzMzLTQwZDUtOGE0Zi1jNjc4N2E3OTBlMGEiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiMTlkYjU0ZDktOTk5ZS00ZDY1LWE2YTUtNGU2NDY1YWQyMGI5IiwiaWF0IjoxNzc2ODk4MjkyLCJleHAiOjE3Nzk0MDgwMDB9.h1wDPxLr7wGMf2wvISxl-FkX9NhkTSnqfXaPZYC3IA8"
N8N_URL = "http://localhost:5678/api/v1"
HEADERS = {"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"}

def test_mission_trigger():
    print("Testing 'PersonaMimic Industrial Loop' webhook...")
    try:
        resp = requests.post(
            "http://localhost:5678/webhook/trigger-mission",
            json={"niche": "Studio AI Products", "goal": "Automated Deployment Standards"},
            timeout=10
        )
        print(f"Webhook response: {resp.status_code}")
        if resp.status_code == 200:
            print("Webhook triggered successfully.")
        else:
            print(f"Failed: {resp.text}")
    except Exception as e:
        print(f"Error testing webhook: {e}")

def list_recent_executions():
    print("\nFetching recent executions to verify studio standards sync...")
    time.sleep(2)  # wait for any triggered workflows to register
    resp = requests.get(f"{N8N_URL}/executions?limit=5", headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json().get("data", [])
        if not data:
            print("No recent executions found.")
        for ex in data:
            wf_id = ex.get("workflowId")
            status = ex.get("status")
            finished = ex.get("finished")
            print(f"Execution {ex.get('id')}: Workflow {wf_id} | Status: {status} | Finished: {finished}")
    else:
        print(f"Failed to fetch executions: {resp.status_code} {resp.text}")

def execute_swarm_monitor():
    print("\nExecuting 'Swarm Monitor' workflow...")
    # Swarm monitor ID is 3
    resp = requests.post(f"{N8N_URL}/workflows/3/execute", headers=HEADERS)
    if resp.status_code == 200:
        print("Swarm monitor executed successfully.")
        ex_id = resp.json().get("data", {}).get("executionId")
        print(f"Execution ID: {ex_id}")
    else:
        print(f"Failed to execute Swarm Monitor: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    test_mission_trigger()
    execute_swarm_monitor()
    list_recent_executions()
