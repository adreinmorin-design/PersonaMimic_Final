# Dre Proprietary
# Copyright (c) 2024 Dre. All rights reserved.
# This software is the confidential and proprietary information of Dre.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you
# entered into with Dre.

"""
Configuration module for ava_autonomous_1866 SaaS project.

This module provides configuration settings for the Personalized Micro-Learning
platform for Remote Healthcare Professionals.
"""

import logging
import os

# Set up logging configuration
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Define configuration class
class Config:
    """
    Configuration class for ava_autonomous_1866 SaaS project.

    Attributes:
        DEBUG (bool): Debug mode flag.
        TESTING (bool): Testing mode flag.
        SECRET_KEY (str): Secret key for encryption.
        DATABASE_URL (str): Database connection URL.
        LOGGING_LEVEL (int): Logging level.
    """

    def __init__(self):
        """
        Initialize configuration settings.
        """
        self.DEBUG = False
        self.TESTING = False
        self.SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")
        self.DATABASE_URL = os.environ.get("DATABASE_URL", "default_database_url")
        self.LOGGING_LEVEL = logging.INFO

    def get_database_url(self):
        """
        Get database connection URL.

        Returns:
            str: Database connection URL.
        """
        try:
            return self.DATABASE_URL
        except Exception as e:
            logging.error(f"Error getting database URL: {str(e)}")
            return None

    def get_secret_key(self):
        """
        Get secret key for encryption.

        Returns:
            str: Secret key.
        """
        try:
            return self.SECRET_KEY
        except Exception as e:
            logging.error(f"Error getting secret key: {str(e)}")
            return None

    def get_logging_level(self):
        """
        Get logging level.

        Returns:
            int: Logging level.
        """
        try:
            return self.LOGGING_LEVEL
        except Exception as e:
            logging.error(f"Error getting logging level: {str(e)}")
            return None


# Create configuration instance
config = Config()

# Define environment-specific configuration settings
class DevelopmentConfig(Config):
    """
    Development configuration settings.
    """

    def __init__(self):
        """
        Initialize development configuration settings.
        """
        super().__init__()
        self.DEBUG = True
        self.LOGGING_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    """
    Production configuration settings.
    """

    def __init__(self):
        """
        Initialize production configuration settings.
        """
        super().__init__()
        self.LOGGING_LEVEL = logging.INFO


class TestingConfig(Config):
    """
    Testing configuration settings.
    """

    def __init__(self):
        """
        Initialize testing configuration settings.
        """
        super().__init__()
        self.TESTING = True
        self.LOGGING_LEVEL = logging.DEBUG


# Define configuration mapping
config_mapping = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}

# Get current environment
env = os.environ.get("ENV", "development")

# Create environment-specific configuration instance
config_instance = config_mapping[env]()

# Update global configuration instance
config = config_instance