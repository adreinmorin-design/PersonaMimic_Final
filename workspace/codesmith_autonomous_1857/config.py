# Dre Proprietary
# Copyright (c) 2024 Dre. All rights reserved.
# This software is the confidential and proprietary information of Dre.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you entered into with Dre.

"""
Configuration module for codesmith_autonomous_1857 SaaS project.

This module provides configuration settings for the Personalized Micro-Learning platform
for Remote Healthcare Workers. It follows Domain-Driven Design (DDD) principles and
includes robust error handling and explicit logging tracing.
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
    Configuration class for codesmith_autonomous_1857 SaaS project.

    Attributes:
        DEBUG (bool): Debug mode flag.
        TESTING (bool): Testing mode flag.
        SECRET_KEY (str): Secret key for encryption.
        DATABASE_URI (str): Database connection URI.
        LEARNING_PATHS (dict): Learning paths configuration.
    """

    def __init__(self):
        self.DEBUG = False
        self.TESTING = False
        self.SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")
        self.DATABASE_URI = os.environ.get("DATABASE_URI", "default_database_uri")
        self.LEARNING_PATHS = {
            "path1": {"name": "Path 1", "description": "Description for Path 1"},
            "path2": {"name": "Path 2", "description": "Description for Path 2"},
        }

    def get_learning_paths(self):
        """
        Returns the learning paths configuration.

        Returns:
            dict: Learning paths configuration.
        """
        try:
            return self.LEARNING_PATHS
        except Exception as e:
            logging.error(f"Error getting learning paths: {str(e)}")
            return {}

    def get_database_uri(self):
        """
        Returns the database connection URI.

        Returns:
            str: Database connection URI.
        """
        try:
            return self.DATABASE_URI
        except Exception as e:
            logging.error(f"Error getting database URI: {str(e)}")
            return ""

# Create a configuration instance
config = Config()

# Define a function to get the configuration instance
def get_config():
    """
    Returns the configuration instance.

    Returns:
        Config: Configuration instance.
    """
    try:
        return config
    except Exception as e:
        logging.error(f"Error getting configuration: {str(e)}")
        return None