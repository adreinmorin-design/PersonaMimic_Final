import requests

BASE_URL = "http://localhost:8000/api"


def check_history():
    try:
        # We might need the security key if it's protected
        # For now let's try a guest call to see if it even exists
        response = requests.get(f"{BASE_URL}/reverse-engineering/history")
        print(f"Status: {response.status_code}")
        print(f"Content: {response.text[:200]}")
    except Exception as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    check_history()
