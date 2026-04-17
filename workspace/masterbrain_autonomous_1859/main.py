# Dre Proprietary
# Copyright (c) 2024 Dre Proprietary. All rights reserved.
# This software is the confidential and proprietary information of Dre Proprietary.
# ("Confidential Information"). You shall not disclose such Confidential Information and shall use it only in accordance with the terms of the license agreement you entered into with Dre Proprietary.

"""
Main entry point for the masterbrain_autonomous_1859 SaaS project.

This module provides the primary interface for interacting with the Micro-SaaS Productivity Utilities.
It utilizes Domain-Driven Design (DDD) principles to ensure a clean, modular, and maintainable architecture.
"""

import logging
from logging.config import dictConfig
from masterbrain_autonomous_1859.domain import DomainService
from masterbrain_autonomous_1859.infrastructure import InfrastructureService
from masterbrain_autonomous_1859.application import ApplicationService

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

    This function initializes the necessary services and begins the execution of the application.
    """
    try:
        # Initialize domain service
        domain_service = DomainService()

        # Initialize infrastructure service
        infrastructure_service = InfrastructureService()

        # Initialize application service
        application_service = ApplicationService(domain_service, infrastructure_service)

        # Start the application
        application_service.start()

    except Exception as e:
        # Log any exceptions that occur during execution
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()