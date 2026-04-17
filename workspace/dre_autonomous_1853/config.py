# Dre Proprietary
# Copyright (c) 2023 Dre Autonomous 1853
# All rights reserved.
# 
# This software is the confidential and proprietary information of Dre Autonomous 1853
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you
# entered into with Dre Autonomous 1853.

"""
Configuration module for dre_autonomous_1853 SaaS project.

This module contains all the configuration settings for the project, including
database connections, API keys, and other environment-specific settings.
"""

import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    """
    Base configuration class.
    """
    DEBUG = False
    TESTING = False
    LOGGING_LEVEL = logging.INFO

    # Database settings
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 5432))
    DB_USERNAME = os.environ.get('DB_USERNAME', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
    DB_NAME = os.environ.get('DB_NAME', 'dre_autonomous_1853')

    # API settings
    API_KEY = os.environ.get('API_KEY', 'default_api_key')
    API_SECRET = os.environ.get('API_SECRET', 'default_api_secret')

    # Micro-learning settings
    MICRO_LEARNING_ENABLED = True
    MICRO_LEARNING_PROVIDER = os.environ.get('MICRO_LEARNING_PROVIDER', 'default_provider')

    def __init__(self):
        """
        Initialize the configuration object.
        """
        try:
            # Load environment variables from .env file
            from dotenv import load_dotenv
            load_dotenv()
        except Exception as e:
            logger.error(f"Error loading environment variables: {e}")

class DevelopmentConfig(Config):
    """
    Development configuration class.
    """
    DEBUG = True
    LOGGING_LEVEL = logging.DEBUG

    def __init__(self):
        """
        Initialize the development configuration object.
        """
        super().__init__()
        try:
            # Load development-specific environment variables
            self.DB_HOST = os.environ.get('DEV_DB_HOST', 'localhost')
            self.DB_PORT = int(os.environ.get('DEV_DB_PORT', 5432))
            self.DB_USERNAME = os.environ.get('DEV_DB_USERNAME', 'postgres')
            self.DB_PASSWORD = os.environ.get('DEV_DB_PASSWORD', 'postgres')
            self.DB_NAME = os.environ.get('DEV_DB_NAME', 'dre_autonomous_1853_dev')
        except Exception as e:
            logger.error(f"Error loading development environment variables: {e}")

class ProductionConfig(Config):
    """
    Production configuration class.
    """
    LOGGING_LEVEL = logging.INFO

    def __init__(self):
        """
        Initialize the production configuration object.
        """
        super().__init__()
        try:
            # Load production-specific environment variables
            self.DB_HOST = os.environ.get('PROD_DB_HOST', 'localhost')
            self.DB_PORT = int(os.environ.get('PROD_DB_PORT', 5432))
            self.DB_USERNAME = os.environ.get('PROD_DB_USERNAME', 'postgres')
            self.DB_PASSWORD = os.environ.get('PROD_DB_PASSWORD', 'postgres')
            self.DB_NAME = os.environ.get('PROD_DB_NAME', 'dre_autonomous_1853_prod')
        except Exception as e:
            logger.error(f"Error loading production environment variables: {e}")

class TestingConfig(Config):
    """
    Testing configuration class.
    """
    TESTING = True
    LOGGING_LEVEL = logging.DEBUG

    def __init__(self):
        """
        Initialize the testing configuration object.
        """
        super().__init__()
        try:
            # Load testing-specific environment variables
            self.DB_HOST = os.environ.get('TEST_DB_HOST', 'localhost')
            self.DB_PORT = int(os.environ.get('TEST_DB_PORT', 5432))
            self.DB_USERNAME = os.environ.get('TEST_DB_USERNAME', 'postgres')
            self.DB_PASSWORD = os.environ.get('TEST_DB_PASSWORD', 'postgres')
            self.DB_NAME = os.environ.get('TEST_DB_NAME', 'dre_autonomous_1853_test')
        except Exception as e:
            logger.error(f"Error loading testing environment variables: {e}")

# Create a dictionary to map configuration classes to their respective environments
config_classes = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

def get_config(env):
    """
    Get the configuration object for the specified environment.

    Args:
        env (str): The environment to get the configuration for.

    Returns:
        Config: The configuration object for the specified environment.
    """
    try:
        return config_classes[env]()
    except KeyError:
        logger.error(f"Invalid environment: {env}")
        return None

# Get the current environment
env = os.environ.get('ENV', 'development')

# Get the configuration object for the current environment
config = get_config(env)

if config is None:
    logger.error("Failed to get configuration object")
else:
    logger.info(f"Using {env} configuration")