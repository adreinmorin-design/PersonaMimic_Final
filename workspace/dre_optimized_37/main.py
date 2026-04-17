# Copyright 2023 Dre Proprietary
# All rights reserved.

"""
main.py

This module serves as the entry point for our SaaS project 'dre_optimized_37'.
It initializes the application, sets up logging, and starts the server.
"""

import logging
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from routes import model_routes, data_routes

# Initialize the FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up CORS middleware to allow cross-origin requests
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    Startup event handler to log when the application starts.
    """
    logger.info("Application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler to log when the application shuts down.
    """
    logger.info("Application shutting down...")

# Include routes
app.include_router(model_routes.router, prefix="/models", tags=["Models"])
app.include_router(data_routes.router, prefix="/data", tags=["Data"])

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting the application...")
    uvicorn.run(app, host="0.0.0.0", port=8000)