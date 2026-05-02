import asyncio
import json
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath("."))

from app.swarm.service import swarm_manager

async def main():
    # Initialize enough to see brains
    await swarm_manager.initialize()
    status = swarm_manager.get_status()
    print(json.dumps(status, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
