# Dre Proprietary
# Copyright (c) 2023, Ava Optimized 2128
# All rights reserved.

"""
Main entry point for Ava Optimized 2128 SaaS project.

This module serves as the central hub for the application, handling
configuration, logging, and initialization of the mental health coaching
service.
"""

import logging
import os
from typing import Dict, List
from ava_optimized_2128.config import Config
from ava_optimized_2128.coach import Coach
from ava_optimized_2128.client import Client
from ava_optimized_2128.utils import load_config, get_logger

# Set up logging configuration
logger = get_logger(__name__)

def load_environment_variables() -> Dict[str, str]:
    """
    Load environment variables from the operating system.

    Returns:
        A dictionary containing the loaded environment variables.
    """
    env_vars = {}
    for var in os.environ:
        env_vars[var] = os.environ[var]
    return env_vars

def load_config_file(config_path: str) -> Config:
    """
    Load the application configuration from a file.

    Args:
        config_path: The path to the configuration file.

    Returns:
        An instance of the Config class containing the loaded configuration.
    """
    try:
        config = load_config(config_path)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

def initialize_coach(config: Config) -> Coach:
    """
    Initialize the mental health coaching service.

    Args:
        config: The application configuration.

    Returns:
        An instance of the Coach class representing the coaching service.
    """
    try:
        coach = Coach(config)
        logger.info("Initialized coaching service")
        return coach
    except Exception as e:
        logger.error(f"Failed to initialize coaching service: {e}")
        raise

def initialize_client(config: Config) -> Client:
    """
    Initialize the client service.

    Args:
        config: The application configuration.

    Returns:
        An instance of the Client class representing the client service.
    """
    try:
        client = Client(config)
        logger.info("Initialized client service")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize client service: {e}")
        raise

def main() -> None:
    """
    Main entry point for the application.
    """
    try:
        # Load environment variables
        env_vars = load_environment_variables()

        # Load configuration file
        config_path = "ava_optimized_2128/config/config.json"
        config = load_config_file(config_path)

        # Initialize coaching service
        coach = initialize_coach(config)

        # Initialize client service
        client = initialize_client(config)

        # Start the application
        logger.info("Starting application")
        coach.start()
        client.start()

        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Application failed to start: {e}")

if __name__ == "__main__":
    main()