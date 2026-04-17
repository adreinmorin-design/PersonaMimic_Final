# Dre Proprietary
# Copyright (c) 2023 Dre Optimized 2056
# All rights reserved.

"""
Main entry point for the Dre Optimized 2056 SaaS project.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
from dre_optimized_2056.domain import ElderlyCareService
from dre_optimized_2056.infrastructure import DatabaseConnection

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a rotating file handler
file_handler = RotatingFileHandler('dre_optimized_2056.log', maxBytes=1024*1024*10, backupCount=5)
file_handler.setLevel(logging.INFO)

# Create a console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.ERROR)

# Create a formatter and attach it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def main():
    """
    Main entry point for the application.
    """
    try:
        # Create a database connection
        db_connection = DatabaseConnection()

        # Create an elderly care service
        elderly_care_service = ElderlyCareService(db_connection)

        # Start the service
        elderly_care_service.start()

        # Run the service in an infinite loop
        while True:
            # Process incoming requests
            elderly_care_service.process_requests()

            # Sleep for a short period
            import time
            time.sleep(1)

    except Exception as e:
        # Log the exception
        logger.error(f"An error occurred: {e}")

        # Re-raise the exception
        raise

if __name__ == "__main__":
    main()