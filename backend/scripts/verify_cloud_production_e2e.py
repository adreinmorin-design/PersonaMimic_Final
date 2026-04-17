import requests

BACKEND_URL = "https://personamimic-backend-303777742757.us-central1.run.app"
SECURITY_KEY = "dre_secure_2026"


def verify_e2e():
    print(f"[*] Starting Cloud E2E Verification for: {BACKEND_URL}")

    # 1. Health Check
    try:
        res = requests.get(BACKEND_URL, timeout=10)
        print(f"[*] Health Check: {res.status_code} - {res.json()}")
    except Exception as e:
        print(f"[ERR] Backend not reachable: {e}")
        return

    # 2. Trigger Autonomous Task: Build & Sell
    # We use a task that instructs the swarm to package and publish.
    task_payload = {
        "task": "Create a high-value '2025 AI SaaS Blueprint' markdown guide, validate it with the adversary, package it as a zip, and publish it to Whop for $1. This is a final end-to-end cloud validation.",
        "brain_id": "MasterBrain",  # Assuming MasterBrain exists or will be created
    }

    headers = {"X-Security-Key": SECURITY_KEY, "Content-Type": "application/json"}

    print("[*] Triggering Autonomous Task: Packaging and Selling...")
    try:
        # First, ensure we have a session or just hit the task endpoint if it's open
        # Let's check the swarm status first
        status_res = requests.get(f"{BACKEND_URL}/swarm/status", headers=headers)
        print(f"[*] Swarm Status: {status_res.status_code}")

        # Triggering the task
        task_res = requests.post(f"{BACKEND_URL}/swarm/task", json=task_payload, headers=headers)
        if task_res.status_code == 200:
            print("[SUCCESS] Task Accepted by Cloud Swarm.")
            print(f"[RESPONSE] {task_res.json()}")
        else:
            print(f"[FAIL] Task rejected: {task_res.status_code} - {task_res.text}")

    except Exception as e:
        print(f"[ERR] Swarm interaction failed: {e}")


if __name__ == "__main__":
    verify_e2e()
