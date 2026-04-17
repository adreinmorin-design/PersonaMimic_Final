# Dre Proprietary
# Copyright (c) 2023 Codesmith Optimized 1772

"""
Main entry point for the Self-Healing API Monitoring SaaS application.

This module serves as the central hub for the application, handling
configuration, logging, and initialization of the monitoring system.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
from codesmith_optimized_1772.config import Config
from codesmith_optimized_1772.monitoring import MonitoringSystem
from codesmith_optimized_1772.healthchecks import HealthChecks
from codesmith_optimized_1772.reporting import ReportingSystem

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        RotatingFileHandler("self_healing_api_monitoring.log", maxBytes=10 * 1024 * 1024, backupCount=5),
        logging.StreamHandler(sys.stdout)
    ]
)

def configure_logging():
    """
    Configure the logging system with the specified settings.
    """
    logging.info("Configuring logging system...")
    try:
        # Set up logging handlers
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                RotatingFileHandler("self_healing_api_monitoring.log", maxBytes=10 * 1024 * 1024, backupCount=5),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logging.info("Logging system configured successfully.")
    except Exception as e:
        logging.error(f"Failed to configure logging system: {e}")

def initialize_monitoring_system(config: Config):
    """
    Initialize the monitoring system with the specified configuration.

    Args:
        config (Config): The configuration object for the monitoring system.

    Returns:
        MonitoringSystem: The initialized monitoring system.
    """
    logging.info("Initializing monitoring system...")
    try:
        # Create a new instance of the monitoring system
        monitoring_system = MonitoringSystem(config)
        logging.info("Monitoring system initialized successfully.")
        return monitoring_system
    except Exception as e:
        logging.error(f"Failed to initialize monitoring system: {e}")
        return None

def initialize_healthchecks(config: Config):
    """
    Initialize the healthchecks system with the specified configuration.

    Args:
        config (Config): The configuration object for the healthchecks system.

    Returns:
        HealthChecks: The initialized healthchecks system.
    """
    logging.info("Initializing healthchecks system...")
    try:
        # Create a new instance of the healthchecks system
        healthchecks = HealthChecks(config)
        logging.info("Healthchecks system initialized successfully.")
        return healthchecks
    except Exception as e:
        logging.error(f"Failed to initialize healthchecks system: {e}")
        return None

def initialize_reporting_system(config: Config):
    """
    Initialize the reporting system with the specified configuration.

    Args:
        config (Config): The configuration object for the reporting system.

    Returns:
        ReportingSystem: The initialized reporting system.
    """
    logging.info("Initializing reporting system...")
    try:
        # Create a new instance of the reporting system
        reporting_system = ReportingSystem(config)
        logging.info("Reporting system initialized successfully.")
        return reporting_system
    except Exception as e:
        logging.error(f"Failed to initialize reporting system: {e}")
        return None

def main():
    """
    Main entry point for the application.

    This function is responsible for initializing the application, including
    configuration, logging, and initialization of the monitoring system.
    """
    logging.info("Starting application...")
    try:
        # Load the configuration
        config = Config()

        # Configure logging
        configure_logging()

        # Initialize the monitoring system
        monitoring_system = initialize_monitoring_system(config)

        # Initialize the healthchecks system
        healthchecks = initialize_healthchecks(config)

        # Initialize the reporting system
        reporting_system = initialize_reporting_system(config)

        # Start the monitoring system
        monitoring_system.start()

        # Start the healthchecks system
        healthchecks.start()

        # Start the reporting system
        reporting_system.start()

        logging.info("Application started successfully.")
    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()