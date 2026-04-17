# Dre Proprietary
# Copyright (c) 2023 Dre Autonomous 1853. All rights reserved.
# This software is the confidential and proprietary information of Dre Autonomous 1853.
# ("Confidential Information"). You shall not disclose such Confidential Information and shall use it only in accordance with the terms of the license agreement you entered into with Dre Autonomous 1853.

"""
Main application entry point for dre_autonomous_1853 SaaS project.
Provides high-performance tool for Personalized Micro-Learning for Remote Healthcare Professionals.
"""

import logging
import os
from datetime import datetime
from typing import Dict

from dre_autonomous_1853.config import Config
from dre_autonomous_1853.domain import Domain
from dre_autonomous_1853.infrastructure import Infrastructure
from dre_autonomous_1853.services import Services

# Initialize logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_config() -> Config:
    """
    Initialize application configuration.

    Returns:
        Config: Application configuration object.
    """
    try:
        config = Config()
        config.load_config()
        return config
    except Exception as e:
        logger.error(f"Error initializing config: {str(e)}")
        raise

def initialize_domain(config: Config) -> Domain:
    """
    Initialize application domain.

    Args:
        config (Config): Application configuration object.

    Returns:
        Domain: Application domain object.
    """
    try:
        domain = Domain(config)
        return domain
    except Exception as e:
        logger.error(f"Error initializing domain: {str(e)}")
        raise

def initialize_infrastructure(config: Config) -> Infrastructure:
    """
    Initialize application infrastructure.

    Args:
        config (Config): Application configuration object.

    Returns:
        Infrastructure: Application infrastructure object.
    """
    try:
        infrastructure = Infrastructure(config)
        return infrastructure
    except Exception as e:
        logger.error(f"Error initializing infrastructure: {str(e)}")
        raise

def initialize_services(domain: Domain, infrastructure: Infrastructure) -> Services:
    """
    Initialize application services.

    Args:
        domain (Domain): Application domain object.
        infrastructure (Infrastructure): Application infrastructure object.

    Returns:
        Services: Application services object.
    """
    try:
        services = Services(domain, infrastructure)
        return services
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        raise

def main() -> None:
    """
    Main application entry point.
    """
    try:
        config = initialize_config()
        domain = initialize_domain(config)
        infrastructure = initialize_infrastructure(config)
        services = initialize_services(domain, infrastructure)

        # Start application
        services.start()
    except Exception as e:
        logger.error(f"Error running application: {str(e)}")
        raise

if __name__ == "__main__":
    main()