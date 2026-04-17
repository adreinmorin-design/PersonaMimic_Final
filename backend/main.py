from dotenv import load_dotenv

from app.core.factory import create_app
from app.core.logging import setup_logging

load_dotenv()

# 2. Configure Structured Logging
setup_logging()

# 3. Create Industrial App
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8055)
