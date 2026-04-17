# Dre Proprietary
# Copyright (c) 2024 Dre Proprietary. All rights reserved.
# This software is the confidential and proprietary information of Dre Proprietary.
# ("Confidential Information"). You shall not disclose such Confidential Information and shall use it only in accordance with the terms of the license agreement you entered into with Dre Proprietary.

"""
Main entry point for the fenko_autonomous_1865 SaaS project.

This module provides the main application logic for the Personalized Micro-Learning tool for Remote Healthcare Workers.
"""

import logging
import os
from typing import Dict

from fenko_autonomous_1865.config import Config
from fenko_autonomous_1865.domain import HealthcareWorker, LearningModule
from fenko_autonomous_1865.infrastructure import DatabaseRepository, LearningModuleRepository
from fenko_autonomous_1865.services import LearningModuleService, PersonalizedLearningService

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main application entry point.

    This function initializes the application, loads the configuration, and starts the main application loop.
    """
    try:
        # Load configuration from environment variables or configuration file
        config = Config.load_config()

        # Initialize database repository
        database_repository = DatabaseRepository(config.database_url)

        # Initialize learning module repository
        learning_module_repository = LearningModuleRepository(config.learning_module_url)

        # Initialize learning module service
        learning_module_service = LearningModuleService(learning_module_repository)

        # Initialize personalized learning service
        personalized_learning_service = PersonalizedLearningService(learning_module_service, database_repository)

        # Start the main application loop
        start_application_loop(personalized_learning_service, database_repository)

    except Exception as e:
        # Log any exceptions that occur during application startup
        logger.error(f"Error starting application: {str(e)}")
        raise

def start_application_loop(personalized_learning_service: PersonalizedLearningService, database_repository: DatabaseRepository):
    """
    Main application loop.

    This function continuously checks for new healthcare workers and assigns personalized learning modules.
    """
    try:
        # Continuously check for new healthcare workers
        while True:
            # Retrieve all healthcare workers from the database
            healthcare_workers: Dict[int, HealthcareWorker] = database_repository.get_all_healthcare_workers()

            # Assign personalized learning modules to each healthcare worker
            for healthcare_worker_id, healthcare_worker in healthcare_workers.items():
                # Retrieve the healthcare worker's learning profile
                learning_profile = database_repository.get_learning_profile(healthcare_worker_id)

                # Assign personalized learning modules based on the healthcare worker's learning profile
                personalized_learning_modules: Dict[int, LearningModule] = personalized_learning_service.assign_learning_modules(learning_profile)

                # Update the healthcare worker's learning profile with the assigned learning modules
                database_repository.update_learning_profile(healthcare_worker_id, personalized_learning_modules)

            # Sleep for a short period before checking for new healthcare workers again
            import time
            time.sleep(60)

    except Exception as e:
        # Log any exceptions that occur during the application loop
        logger.error(f"Error in application loop: {str(e)}")
        raise

if __name__ == "__main__":
    main()