import json

import requests

base_url = "http://localhost:8055"


def test_endpoints():
    print("--- TESTING SYSTEM ENDPOINTS ---")

    try:
        # 1. Health
        health = requests.get(f"{base_url}/system/health", timeout=10)
        print(f"Health Status [{health.status_code}]: {json.dumps(health.json(), indent=2)}")

        # 2. Intelligence
        intel = requests.get(f"{base_url}/system/intelligence", timeout=10)
        print(f"Intelligence Status [{intel.status_code}]: {json.dumps(intel.json(), indent=2)}")

    except Exception as e:
        print(f"Connection Failed: {e}")


if __name__ == "__main__":
    test_endpoints()
