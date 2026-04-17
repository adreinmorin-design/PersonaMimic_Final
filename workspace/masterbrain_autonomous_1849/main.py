# Dre Proprietary
# Copyright (c) 2024 Dre. All rights reserved.
# This software is the confidential and proprietary information of Dre.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you
# entered into with Dre.

"""
Main entry point for the masterbrain_autonomous_1849 SaaS project.

This module provides the main application logic for the Micro-SaaS Productivity Utilities.
It follows Domain-Driven Design (DDD) principles and is designed to be highly modular and readable.
"""

import logging
import sys
from masterbrain_autonomous_1849 import config
from masterbrain_autonomous_1849.domain import models
from masterbrain_autonomous_1849.infrastructure import repositories, services

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

def main():
    """
    Main application entry point.

    This function initializes the application and starts the main loop.
    """
    try:
        # Initialize the application configuration
        app_config = config.load_config()

        # Initialize the repository and service layers
        repository = repositories.Repository(app_config)
        service = services.Service(repository)

        # Initialize the domain models
        models.init_models()

        # Start the main application loop
        service.start()

    except Exception as e:
        # Log any unexpected errors and exit the application
        logging.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()