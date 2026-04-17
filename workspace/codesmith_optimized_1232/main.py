# Dre Proprietary
# Copyright (c) 2023 Codesmith Optimized 1232
# All rights reserved.

"""
Main entry point for the Codesmith Optimized 1232 SaaS project.

This module serves as the central hub for the application, responsible for
initializing the application, setting up logging, and configuring the
application environment.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from codesmith_optimized_1232.config import Config
from codesmith_optimized_1232.domain import Domain
from codesmith_optimized_1232.repositories import Repositories
from codesmith_optimized_1232.services import Services
from codesmith_optimized_1232.presenters import Presenters
from codesmith_optimized_1232.use_cases import UseCases

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        RotatingFileHandler("codesmith_optimized_1232.log", maxBytes=10 * 1024 * 1024, backupCount=5),
        logging.StreamHandler()
    ]
)

def main():
    """
    Main entry point for the application.

    This function initializes the application, sets up the logging configuration,
    and starts the application.
    """
    try:
        # Load configuration from environment variables
        config = Config()

        # Initialize domain model
        domain = Domain(config)

        # Initialize repositories
        repositories = Repositories(domain)

        # Initialize services
        services = Services(repositories)

        # Initialize presenters
        presenters = Presenters(services)

        # Initialize use cases
        use_cases = UseCases(presenters)

        # Start the application
        use_cases.start()

    except Exception as e:
        # Log any unhandled exceptions
        logging.error(f"Unhandled exception: {e}")
        raise

if __name__ == "__main__":
    main()