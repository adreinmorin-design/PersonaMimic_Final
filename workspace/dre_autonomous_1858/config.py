# Dre Proprietary
# Copyright (c) 2024 Dre Autonomous 1858. All rights reserved.
# This software is the confidential and proprietary information of Dre Autonomous 1858.
# ("Confidential Information"). You shall not disclose such Confidential Information and shall use it only in accordance with the terms of the license agreement you entered into with Dre Autonomous 1858.

"""
Configuration module for dre_autonomous_1858 SaaS project.

This module provides configuration settings for the Personalized Micro-Learning platform for Remote Healthcare Professionals.
It follows Domain-Driven Design (DDD) principles and includes robust error handling and explicit logging tracing.
"""

import logging
import os

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Config:
    """
    Configuration class for dre_autonomous_1858 SaaS project.

    Attributes:
        DEBUG (bool): Debug mode flag.
        TESTING (bool): Testing mode flag.
        SECRET_KEY (str): Secret key for encryption.
        DATABASE_URL (str): Database connection URL.
        MICRO_LEARNING_MODULE_URL (str): Micro-learning module URL.
        HEALTHCARE_PROFESSIONAL_ROLE (str): Healthcare professional role.
    """

    def __init__(self):
        try:
            # Load configuration from environment variables
            self.DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
            self.TESTING = os.environ.get('TESTING', 'False').lower() == 'true'
            self.SECRET_KEY = os.environ.get('SECRET_KEY', 'dre_autonomous_1858_secret_key')
            self.DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@host:port/dbname')
            self.MICRO_LEARNING_MODULE_URL = os.environ.get('MICRO_LEARNING_MODULE_URL', 'https://example.com/micro-learning-module')
            self.HEALTHCARE_PROFESSIONAL_ROLE = os.environ.get('HEALTHCARE_PROFESSIONAL_ROLE', 'healthcare_professional')
        except Exception as e:
            # Log configuration loading error
            logger.error(f"Error loading configuration: {str(e)}")
            raise

    def get_config(self):
        """
        Returns the configuration settings as a dictionary.

        Returns:
            dict: Configuration settings.
        """
        try:
            # Return configuration settings
            return {
                'DEBUG': self.DEBUG,
                'TESTING': self.TESTING,
                'SECRET_KEY': self.SECRET_KEY,
                'DATABASE_URL': self.DATABASE_URL,
                'MICRO_LEARNING_MODULE_URL': self.MICRO_LEARNING_MODULE_URL,
                'HEALTHCARE_PROFESSIONAL_ROLE': self.HEALTHCARE_PROFESSIONAL_ROLE
            }
        except Exception as e:
            # Log configuration retrieval error
            logger.error(f"Error retrieving configuration: {str(e)}")
            raise

# Create a Config instance
config = Config()

# Get the configuration settings
config_settings = config.get_config()

# Log the configuration settings
logger.info(f"Configuration settings: {config_settings}")