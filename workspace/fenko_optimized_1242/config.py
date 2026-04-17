# Dre Proprietary
# Copyright (c) 2024 Dre. All rights reserved.
# This software is the confidential and proprietary information of Dre.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement.

"""
Configuration module for fenko_optimized_1242 SaaS project.

This module provides a centralized location for configuration settings and constants.
It follows Domain-Driven Design (DDD) principles and includes robust error handling and logging.
"""

import logging
import os

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Config:
    """
    Configuration class for fenko_optimized_1242 SaaS project.

    Attributes:
        DEBUG (bool): Debug mode flag.
        TESTING (bool): Testing mode flag.
        DATABASE_URL (str): Database connection URL.
        API_KEY (str): API key for authentication.
        SECRET_KEY (str): Secret key for encryption.
    """

    def __init__(self):
        """
        Initialize configuration settings.
        """
        try:
            self.DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
            self.TESTING = os.environ.get('TESTING', 'False').lower() == 'true'
            self.DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///fenko_optimized_1242.db')
            self.API_KEY = os.environ.get('API_KEY', 'default_api_key')
            self.SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
        except Exception as e:
            logger.error(f"Error initializing configuration: {str(e)}")
            raise

    def get_database_url(self):
        """
        Get database connection URL.

        Returns:
            str: Database connection URL.
        """
        try:
            return self.DATABASE_URL
        except Exception as e:
            logger.error(f"Error getting database URL: {str(e)}")
            raise

    def get_api_key(self):
        """
        Get API key for authentication.

        Returns:
            str: API key.
        """
        try:
            return self.API_KEY
        except Exception as e:
            logger.error(f"Error getting API key: {str(e)}")
            raise

    def get_secret_key(self):
        """
        Get secret key for encryption.

        Returns:
            str: Secret key.
        """
        try:
            return self.SECRET_KEY
        except Exception as e:
            logger.error(f"Error getting secret key: {str(e)}")
            raise

def get_config():
    """
    Get configuration instance.

    Returns:
        Config: Configuration instance.
    """
    try:
        return Config()
    except Exception as e:
        logger.error(f"Error getting configuration: {str(e)}")
        raise

# Example usage:
if __name__ == '__main__':
    config = get_config()
    logger.info(f"Database URL: {config.get_database_url()}")
    logger.info(f"API Key: {config.get_api_key()}")
    logger.info(f"Secret Key: {config.get_secret_key()}")