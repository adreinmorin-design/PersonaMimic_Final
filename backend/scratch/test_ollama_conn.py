import aiohttp
import asyncio

async def test():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:11434/api/tags", timeout=5) as res:
                print(f"Status: {res.status}")
                data = await res.json()
                print(f"Models: {len(data.get('models', []))}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
