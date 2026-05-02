import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()


async def test_whop_connectivity():
    api_key = os.getenv("WHOP_API_KEY")

    if not api_key or "your_whop_key" in api_key:
        print("[FAIL] WHOP_API_KEY not found or still a placeholder in .env")
        return

    print(f"[*] Testing Whop API connectivity with key: {api_key[:10]}...")

    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            # Attempt to fetch memberships or any basic endpoint
            response = await client.get("https://api.whop.com/api/v2/memberships", headers=headers)

            if response.status_code == 200:
                print("[SUCCESS] Whop API Connection Validated.")
                data = response.json()
                members_count = len(data.get("data", []))
                print(f"[INFO] Successfully retrieved {members_count} recent memberships.")
            elif response.status_code == 401:
                print(
                    f"[FAIL] Unauthorized: Your API key appears invalid. (Status: {response.status_code})"
                )
            else:
                print(f"[WARN] Unexpected response: {response.status_code}")
                print(f"Body: {response.text[:200]}")

        except Exception as e:
            print(f"[ERR] Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_whop_connectivity())
