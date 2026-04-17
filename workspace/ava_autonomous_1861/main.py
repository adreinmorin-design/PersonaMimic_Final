# Dre Proprietary
# Copyright (c) 2024 Dre. All rights reserved.
# This software is the confidential and proprietary information of Dre.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you
# entered into with Dre.

"""
Main entry point for the ava_autonomous_1861 SaaS project.

This module provides the main application logic for the Personalized Micro-Learning
tool for Remote Healthcare Professionals.
"""

import logging
import sys
from ava_autonomous_1861.domain import models
from ava_autonomous_1861.domain.services import LearningPathService, UserService
from ava_autonomous_1861.infrastructure import repositories

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

def main():
    """
    Main application entry point.

    This function initializes the application, sets up the necessary services,
    and starts the learning path recommendation process.
    """
    try:
        # Initialize the user repository
        user_repository = repositories.UserRepository()

        # Initialize the learning path repository
        learning_path_repository = repositories.LearningPathRepository()

        # Initialize the user service
        user_service = UserService(user_repository)

        # Initialize the learning path service
        learning_path_service = LearningPathService(learning_path_repository, user_service)

        # Get the current user
        current_user = user_service.get_current_user()

        # Get the recommended learning path for the current user
        recommended_learning_path = learning_path_service.get_recommended_learning_path(current_user)

        # Log the recommended learning path
        logging.info(f"Recommended learning path for user {current_user.id}: {recommended_learning_path.id}")

        # Start the learning path
        learning_path_service.start_learning_path(recommended_learning_path, current_user)

    except Exception as e:
        # Log any exceptions that occur during the application execution
        logging.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()