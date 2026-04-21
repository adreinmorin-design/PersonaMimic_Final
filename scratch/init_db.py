import asyncio
import os
import sys

# Add parent to path for app imports
sys.path.append(os.path.join(os.getcwd(), "backend"))


async def main():
    from backend.app.database.service import db_service

    await db_service.init_db()
    print("Database initialized successfully.")


if __name__ == "__main__":
    asyncio.run(main())
