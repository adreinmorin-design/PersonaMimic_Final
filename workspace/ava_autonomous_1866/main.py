# Dre Proprietary
# Copyright (c) 2024 Dre Proprietary. All rights reserved.
# This software is the confidential and proprietary information of Dre Proprietary.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you
# entered into with Dre Proprietary.

"""
Main entry point for the Ava Autonomous 1866 SaaS project.

This module provides the main application logic for the personalized micro-learning
platform for remote healthcare professionals.
"""

import logging
import os
from ava_autonomous_1866.config import Config
from ava_autonomous_1866.domain import Domain
from ava_autonomous_1866.infrastructure import Infrastructure
from ava_autonomous_1866.application import Application

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("ava_autonomous_1866.log"), logging.StreamHandler()],
)

def main():
    """
    Main application entry point.

    This function initializes the application and starts the main loop.
    """
    try:
        # Load configuration
        config = Config.load_config()

        # Initialize domain
        domain = Domain(config)

        # Initialize infrastructure
        infrastructure = Infrastructure(config)

        # Initialize application
        application = Application(domain, infrastructure)

        # Start application
        application.start()

    except Exception as e:
        # Log any exceptions that occur during application startup
        logging.error(f"Error starting application: {str(e)}")
        raise

if __name__ == "__main__":
    main()