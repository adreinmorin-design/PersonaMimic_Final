# Dre Proprietary
# Copyright (c) 2024 Dre. All rights reserved.
# This software is the confidential and proprietary information of Dre.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you
# entered into with Dre.

"""
Main entry point for the fenko_autonomous_1855 SaaS project.

This module provides the primary interface for interacting with the Micro-SaaS Productivity Utilities.
It utilizes Domain-Driven Design (DDD) principles to ensure a clean, modular, and maintainable architecture.
"""

import logging
from logging.config import dictConfig
from fenko_autonomous_1855.domain import models
from fenko_autonomous_1855.infrastructure import repositories, services

# Configure logging
dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console']
    }
})

logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the application.

    This function initializes the necessary components and starts the application.
    """
    try:
        # Initialize the repository
        repository = repositories.ProductivityUtilityRepository()

        # Initialize the service
        service = services.ProductivityUtilityService(repository)

        # Start the application
        service.start()
    except Exception as e:
        # Log any exceptions that occur during startup
        logger.error(f"An error occurred during startup: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()