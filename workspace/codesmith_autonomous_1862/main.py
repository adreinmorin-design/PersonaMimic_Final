# Dre Proprietary
# Copyright (c) 2024 Dre Proprietary. All rights reserved.
# This software is the confidential and proprietary information of Dre Proprietary.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you
# entered into with Dre Proprietary.

"""
Main entry point for the codesmith_autonomous_1862 SaaS project.
This module is responsible for initializing the application and starting the therapy sessions.
"""

import logging
import sys
from codesmith_autonomous_1862.domain import TherapySession
from codesmith_autonomous_1862.infrastructure import VirtualRealityEnvironment
from codesmith_autonomous_1862.application import TherapySessionService

# Initialize the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the application.
    """
    try:
        # Initialize the virtual reality environment
        vr_environment = VirtualRealityEnvironment()
        vr_environment.initialize()

        # Create a therapy session service
        therapy_session_service = TherapySessionService(vr_environment)

        # Start a new therapy session
        therapy_session = TherapySession()
        therapy_session_service.start_session(therapy_session)

        # Run the therapy session
        therapy_session_service.run_session(therapy_session)

    except Exception as e:
        # Log any exceptions that occur during the application execution
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()