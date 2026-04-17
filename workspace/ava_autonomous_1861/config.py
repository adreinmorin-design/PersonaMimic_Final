# Dre Proprietary
# Copyright (c) 2024 Dre. All rights reserved.
# This software is the confidential and proprietary information of Dre.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you
# entered into with Dre.

"""
Configuration module for ava_autonomous_1861 SaaS project.

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
    Configuration class for ava_autonomous_1861 SaaS project.

    Attributes:
        DEBUG (bool): Debug mode flag.
        TESTING (bool): Testing mode flag.
        SECRET_KEY (str): Secret key for encryption.
        SQLALCHEMY_DATABASE_URI (str): Database connection URI.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Flag to track modifications.
        LOGGING_LEVEL (int): Logging level.
    """

    def __init__(self):
        """
        Initialize configuration settings.
        """
        self.DEBUG = False
        self.TESTING = False
        self.SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")
        self.SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL", "sqlite:///ava_autonomous_1861.db"
        )
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.LOGGING_LEVEL = logging.INFO

    def get_config(self):
        """
        Get configuration settings as a dictionary.

        Returns:
            dict: Configuration settings.
        """
        return {
            "DEBUG": self.DEBUG,
            "TESTING": self.TESTING,
            "SECRET_KEY": self.SECRET_KEY,
            "SQLALCHEMY_DATABASE_URI": self.SQLALCHEMY_DATABASE_URI,
            "SQLALCHEMY_TRACK_MODIFICATIONS": self.SQLALCHEMY_TRACK_MODIFICATIONS,
            "LOGGING_LEVEL": self.LOGGING_LEVEL,
        }

# Define development configuration
class DevelopmentConfig(Config):
    """
    Development configuration class.

    Attributes:
        DEBUG (bool): Debug mode flag.
    """

    def __init__(self):
        """
        Initialize development configuration settings.
        """
        super().__init__()
        self.DEBUG = True
        self.LOGGING_LEVEL = logging.DEBUG

# Define production configuration
class ProductionConfig(Config):
    """
    Production configuration class.

    Attributes:
        LOGGING_LEVEL (int): Logging level.
    """

    def __init__(self):
        """
        Initialize production configuration settings.
        """
        super().__init__()
        self.LOGGING_LEVEL = logging.INFO

# Define testing configuration
class TestingConfig(Config):
    """
    Testing configuration class.

    Attributes:
        TESTING (bool): Testing mode flag.
    """

    def __init__(self):
        """
        Initialize testing configuration settings.
        """
        super().__init__()
        self.TESTING = True
        self.LOGGING_LEVEL = logging.DEBUG

# Define configuration factory function
def get_config(env):
    """
    Get configuration instance based on environment.

    Args:
        env (str): Environment name.

    Returns:
        Config: Configuration instance.
    """
    try:
        if env == "development":
            return DevelopmentConfig()
        elif env == "production":
            return ProductionConfig()
        elif env == "testing":
            return TestingConfig()
        else:
            raise ValueError("Invalid environment")
    except Exception as e:
        logging.error(f"Error getting configuration: {str(e)}")
        raise

# Example usage:
if __name__ == "__main__":
    config = get_config("development")
    print(config.get_config())