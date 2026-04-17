# Copyright 2023 Dre Proprietary
# All rights reserved.

"""
main.py

This module serves as the entry point for the ava_optimized_1923 SaaS application, a high-efficiency industrial tool designed for Micro-SaaS Productivity Utilities. It initializes the application and sets up the necessary components.
"""

import logging
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastAPI app instance
app = FastAPI()

# Add CORS middleware to allow cross-origin requests
origins = ["http://localhost:3000", "http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and initialize the core components
from routes import tasks, users

@app.on_event("startup")
async def startup_event():
    """
    Startup event handler for initializing application resources.
    """
    try:
        logger.info("Initializing application...")
        
        # Initialize database connection (placeholder for actual DB initialization)
        # await db.initialize_db()
        
        logger.info("Application initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler for cleaning up resources.
    """
    try:
        logger.info("Shutting down application...")
        
        # Close database connection (placeholder for actual DB cleanup)
        # await db.close_db()
        
        logger.info("Application shut down successfully.")
    except Exception as e:
        logger.error(f"Failed to shutdown application: {e}")
        raise

# Include routes
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(users.router, prefix="/users", tags=["users"])

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting the FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)