# Dre Proprietary
# Copyright (c) 2024 Dre. All rights reserved.
# This software is the confidential and proprietary information of Dre.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you
# entered into with Dre.

"""
Configuration module for codesmith_autonomous_1852.

This module provides configuration settings for the codesmith_autonomous_1852 application.
It includes settings for database connections, API endpoints, and other application-specific
configurations.

Classes:
    Config

Functions:
    get_config
"""

import logging
import os
from typing import Dict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    """
    Configuration class for codesmith_autonomous_1852.

    This class provides a centralized location for application configuration settings.
    It includes settings for database connections, API endpoints, and other application-specific
    configurations.

    Attributes:
        db_host (str): Database host
        db_port (int): Database port
        db_username (str): Database username
        db_password (str): Database password
        db_name (str): Database name
        api_endpoint (str): API endpoint
        api_key (str): API key
    """

    def __init__(self):
        """
        Initializes the Config class.

        Sets up the configuration settings for the application.
        """
        self.db_host = os.environ.get('DB_HOST', 'localhost')
        self.db_port = int(os.environ.get('DB_PORT', 5432))
        self.db_username = os.environ.get('DB_USERNAME', 'codesmith')
        self.db_password = os.environ.get('DB_PASSWORD', 'codesmith')
        self.db_name = os.environ.get('DB_NAME', 'codesmith_autonomous_1852')
        self.api_endpoint = os.environ.get('API_ENDPOINT', 'https://api.codesmith.com')
        self.api_key = os.environ.get('API_KEY', 'your_api_key_here')

    def get_db_config(self) -> Dict:
        """
        Returns the database configuration settings.

        Returns:
            Dict: Database configuration settings
        """
        try:
            return {
                'host': self.db_host,
                'port': self.db_port,
                'username': self.db_username,
                'password': self.db_password,
                'name': self.db_name
            }
        except Exception as e:
            logger.error(f"Error getting database configuration: {str(e)}")
            raise

    def get_api_config(self) -> Dict:
        """
        Returns the API configuration settings.

        Returns:
            Dict: API configuration settings
        """
        try:
            return {
                'endpoint': self.api_endpoint,
                'key': self.api_key
            }
        except Exception as e:
            logger.error(f"Error getting API configuration: {str(e)}")
            raise

def get_config() -> Config:
    """
    Returns an instance of the Config class.

    Returns:
        Config: Config instance
    """
    try:
        return Config()
    except Exception as e:
        logger.error(f"Error getting configuration: {str(e)}")
        raise