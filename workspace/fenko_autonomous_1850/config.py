# Dre Proprietary
# Copyright (c) 2024 Fenko Autonomous 1850

"""
Config module for Fenko Autonomous 1850 SaaS project.

This module contains configuration settings for the application.
"""

import logging
import os
from typing import Dict, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    """
    Base configuration class.

    This class provides a basic structure for configuration settings.
    """

    def __init__(self):
        self.app_name = "Fenko Autonomous 1850"
        self.app_version = "1.0.0"
        self.app_description = "High-performance tool for Micro-SaaS Productivity Utilities"

        # Database configuration
        self.db_host = os.environ.get("DB_HOST", "localhost")
        self.db_port = int(os.environ.get("DB_PORT", 5432))
        self.db_username = os.environ.get("DB_USERNAME", "postgres")
        self.db_password = os.environ.get("DB_PASSWORD", "password")
        self.db_name = os.environ.get("DB_NAME", "fenko_autonomous_1850")

        # API configuration
        self.api_key = os.environ.get("API_KEY", "secret_key")
        self.api_secret = os.environ.get("API_SECRET", "secret_secret")

        # Logging configuration
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")
        self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def get_db_config(self) -> Dict:
        """
        Returns database configuration as a dictionary.

        :return: Database configuration dictionary
        """
        return {
            "host": self.db_host,
            "port": self.db_port,
            "username": self.db_username,
            "password": self.db_password,
            "name": self.db_name,
        }

    def get_api_config(self) -> Dict:
        """
        Returns API configuration as a dictionary.

        :return: API configuration dictionary
        """
        return {
            "key": self.api_key,
            "secret": self.api_secret,
        }

    def get_log_config(self) -> Dict:
        """
        Returns logging configuration as a dictionary.

        :return: Logging configuration dictionary
        """
        return {
            "level": self.log_level,
            "format": self.log_format,
        }

class DevConfig(Config):
    """
    Development configuration class.

    This class extends the base configuration class and provides settings specific to development environment.
    """

    def __init__(self):
        super().__init__()

        # Development-specific settings
        self.debug = True
        self.testing = True

class ProdConfig(Config):
    """
    Production configuration class.

    This class extends the base configuration class and provides settings specific to production environment.
    """

    def __init__(self):
        super().__init__()

        # Production-specific settings
        self.debug = False
        self.testing = False

def get_config(env: str = "dev") -> Config:
    """
    Returns configuration instance based on environment.

    :param env: Environment (dev, prod, etc.)
    :return: Configuration instance
    """
    config_map = {
        "dev": DevConfig(),
        "prod": ProdConfig(),
    }

    if env not in config_map:
        raise ValueError(f"Invalid environment: {env}")

    return config_map[env]

# Example usage
if __name__ == "__main__":
    config = get_config("dev")
    logger.info(config.get_db_config())
    logger.info(config.get_api_config())
    logger.info(config.get_log_config())