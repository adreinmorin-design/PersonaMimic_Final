# Dre Proprietary
# Copyright (c) 2024 Masterbrain Autonomous
# All rights reserved.

"""
Main entry point for Masterbrain Autonomous 1864 SaaS project.
"""

import logging
import os
import sys
from typing import Dict, List
from masterbrain_autonomous_1864.core import config, services, utils
from masterbrain_autonomous_1864.core.domain import models, repositories

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

def load_config() -> Dict:
    """
    Load application configuration from environment variables.
    """
    try:
        config_data = config.load_config()
        return config_data
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        sys.exit(1)

def initialize_services(config_data: Dict) -> None:
    """
    Initialize services based on application configuration.
    """
    try:
        services.initialize_services(config_data)
    except Exception as e:
        logging.error(f"Failed to initialize services: {e}")
        sys.exit(1)

def create_database() -> None:
    """
    Create database schema based on domain models.
    """
    try:
        models.create_tables()
    except Exception as e:
        logging.error(f"Failed to create database schema: {e}")
        sys.exit(1)

def run_app() -> None:
    """
    Run the application.
    """
    try:
        # Load configuration
        config_data = load_config()

        # Initialize services
        initialize_services(config_data)

        # Create database schema
        create_database()

        # Run application logic
        services.run_services()

        # Log application exit
        logging.info("Application exited successfully.")
    except Exception as e:
        logging.error(f"Application failed: {e}")
        sys.exit(1)

def main() -> None:
    """
    Main entry point for the application.
    """
    try:
        # Run application
        run_app()
    except KeyboardInterrupt:
        logging.info("Application exited due to keyboard interrupt.")
    except Exception as e:
        logging.error(f"Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()