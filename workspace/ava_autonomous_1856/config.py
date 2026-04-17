# Dre Proprietary
# Copyright (c) 2024 Dre. All rights reserved.
# This software is the confidential and proprietary information of Dre.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you entered into with Dre.

import logging
import os

# Set up logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class Config:
    """
    Configuration class for ava_autonomous_1856 SaaS project.

    Attributes:
        DEBUG (bool): Debug mode flag.
        TESTING (bool): Testing mode flag.
        LOG_LEVEL (str): Logging level.
        DATABASE_URL (str): Database connection URL.
        API_KEY (str): API key for authentication.
        SECRET_KEY (str): Secret key for encryption.
    """

    def __init__(self):
        """
        Initialize configuration settings.
        """
        self.DEBUG = False
        self.TESTING = False
        self.LOG_LEVEL = 'INFO'
        self.DATABASE_URL = 'postgresql://user:password@host:port/dbname'
        self.API_KEY = 'your_api_key_here'
        self.SECRET_KEY = 'your_secret_key_here'

    def get_database_url(self):
        """
        Get database connection URL.

        Returns:
            str: Database connection URL.
        """
        try:
            return os.environ.get('DATABASE_URL', self.DATABASE_URL)
        except Exception as e:
            logging.error(f'Error getting database URL: {e}')
            return None

    def get_api_key(self):
        """
        Get API key for authentication.

        Returns:
            str: API key.
        """
        try:
            return os.environ.get('API_KEY', self.API_KEY)
        except Exception as e:
            logging.error(f'Error getting API key: {e}')
            return None

    def get_secret_key(self):
        """
        Get secret key for encryption.

        Returns:
            str: Secret key.
        """
        try:
            return os.environ.get('SECRET_KEY', self.SECRET_KEY)
        except Exception as e:
            logging.error(f'Error getting secret key: {e}')
            return None

    def get_log_level(self):
        """
        Get logging level.

        Returns:
            str: Logging level.
        """
        try:
            return os.environ.get('LOG_LEVEL', self.LOG_LEVEL)
        except Exception as e:
            logging.error(f'Error getting log level: {e}')
            return None

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

class ProductionConfig(Config):
    """
    Production configuration class.
    """

    def __init__(self):
        """
        Initialize production configuration settings.
        """
        super().__init__()

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

# Create configuration instance
config = Config()

# Create development configuration instance
development_config = DevelopmentConfig()

# Create production configuration instance
production_config = ProductionConfig()

# Create testing configuration instance
testing_config = TestingConfig()