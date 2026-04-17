# Dre Proprietary
# Copyright (c) 2024 Dre. All rights reserved.
# This software is the confidential and proprietary information of Dre.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you entered into with Dre.

"""
Configuration module for ava_autonomous_1846 SaaS project.

This module provides configuration settings for the Personalized Micro-Learning platform
for Remote Healthcare Workers. It follows Domain-Driven Design (DDD) principles and
includes robust error handling and explicit logging tracing.
"""

import logging
import os

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Config:
    """
    Configuration class for ava_autonomous_1846 SaaS project.

    Attributes:
        DEBUG (bool): Debug mode flag.
        TESTING (bool): Testing mode flag.
        SECRET_KEY (str): Secret key for encryption.
        DATABASE_URL (str): Database connection URL.
        MICRO_LEARNING_MODULE_URL (str): Micro-learning module URL.
        HEALTHCARE_WORKER_ROLE (str): Healthcare worker role.
    """

    def __init__(self):
        """
        Initialize configuration settings.
        """
        try:
            self.DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
            self.TESTING = os.environ.get('TESTING', 'False').lower() == 'true'
            self.SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
            self.DATABASE_URL = os.environ.get('DATABASE_URL', 'default_database_url')
            self.MICRO_LEARNING_MODULE_URL = os.environ.get('MICRO_LEARNING_MODULE_URL', 'default_micro_learning_module_url')
            self.HEALTHCARE_WORKER_ROLE = os.environ.get('HEALTHCARE_WORKER_ROLE', 'default_healthcare_worker_role')
        except Exception as e:
            logger.error(f"Error initializing configuration settings: {str(e)}")
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

    def get_micro_learning_module_url(self):
        """
        Get micro-learning module URL.

        Returns:
            str: Micro-learning module URL.
        """
        try:
            return self.MICRO_LEARNING_MODULE_URL
        except Exception as e:
            logger.error(f"Error getting micro-learning module URL: {str(e)}")
            raise

    def get_healthcare_worker_role(self):
        """
        Get healthcare worker role.

        Returns:
            str: Healthcare worker role.
        """
        try:
            return self.HEALTHCARE_WORKER_ROLE
        except Exception as e:
            logger.error(f"Error getting healthcare worker role: {str(e)}")
            raise

# Create a configuration instance
config = Config()