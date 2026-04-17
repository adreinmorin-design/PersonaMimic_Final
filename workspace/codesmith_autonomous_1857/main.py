# Dre Proprietary
# Copyright (c) 2024 Dre Proprietary. All rights reserved.
# This software is the confidential and proprietary information of Dre Proprietary.
# ("Confidential Information"). You shall not disclose such Confidential Information and shall use it only in accordance with the terms of the license agreement you entered into with Dre Proprietary.

"""
Main entry point for the codesmith_autonomous_1857 SaaS project.

This module provides the primary interface for the Personalized Micro-Learning tool for Remote Healthcare Workers.
It utilizes Domain-Driven Design (DDD) principles to ensure a modular, maintainable, and scalable architecture.
"""

import logging
from logging.config import dictConfig
from codesmith_autonomous_1857.domain import HealthcareWorker, LearningModule
from codesmith_autonomous_1857.infrastructure import DatabaseRepository, LearningModuleRepository
from codesmith_autonomous_1857.application import LearningModuleService

# Configure logging
dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console']
    }
})

def main():
    """
    Main entry point for the application.

    This function initializes the necessary components and starts the learning module service.
    """
    try:
        # Initialize database repository
        database_repository = DatabaseRepository()

        # Initialize learning module repository
        learning_module_repository = LearningModuleRepository(database_repository)

        # Initialize learning module service
        learning_module_service = LearningModuleService(learning_module_repository)

        # Create a healthcare worker
        healthcare_worker = HealthcareWorker("John Doe", "johndoe@example.com")

        # Create a learning module
        learning_module = LearningModule("Introduction to Remote Healthcare", "This is a sample learning module.")

        # Add the learning module to the healthcare worker's learning plan
        learning_module_service.add_learning_module(healthcare_worker, learning_module)

        # Start the learning module service
        learning_module_service.start()

    except Exception as e:
        # Log any exceptions that occur during execution
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()