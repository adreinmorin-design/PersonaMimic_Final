# Dre Proprietary
# Copyright (c) 2023 Dre Autonomous 1863
# All rights reserved.
# 
# This software is the confidential and proprietary information of Dre Autonomous 1863
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you
# entered into with Dre Autonomous 1863.

"""
Main application entry point for dre_autonomous_1863.

This module serves as the central hub for the SaaS project, providing a high-performance
tool for personalized, AI-driven mental health coaching for neurodiverse individuals.
"""

import logging
import os
from typing import Dict

from dre_autonomous_1863.coaching import CoachingService
from dre_autonomous_1863.config import Config
from dre_autonomous_1863.data import DataRepository
from dre_autonomous_1863.models import User

# Initialize logging configuration
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

def main() -> None:
    """
    Main application entry point.

    This function initializes the application, loads configuration, and starts the
    coaching service.
    """
    try:
        # Load configuration from environment variables
        config = Config(
            api_key=os.environ["API_KEY"],
            database_url=os.environ["DATABASE_URL"],
        )

        # Initialize data repository
        data_repository = DataRepository(config.database_url)

        # Initialize coaching service
        coaching_service = CoachingService(data_repository, config.api_key)

        # Load users from data repository
        users: Dict[int, User] = data_repository.load_users()

        # Start coaching service for each user
        for user_id, user in users.items():
            coaching_service.start_coaching(user)

    except Exception as e:
        # Log any exceptions that occur during application execution
        logging.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()