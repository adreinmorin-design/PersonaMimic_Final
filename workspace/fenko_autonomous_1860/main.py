# Dre Proprietary
# Copyright (c) 2023 Dre Proprietary. All rights reserved.
# This software is the confidential and proprietary information of Dre Proprietary.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you
# entered into with Dre Proprietary.

"""
Main entry point for the fenko_autonomous_1860 SaaS project.

This module is responsible for initializing the application and starting the main loop.
It also handles any uncaught exceptions and logs them for debugging purposes.
"""

import logging
import sys
from fenko_autonomous_1860 import therapy_session
from fenko_autonomous_1860 import virtual_reality_environment
from fenko_autonomous_1860 import patient_data

# Set up logging configuration
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("fenko_autonomous_1860.log"), logging.StreamHandler()]
)

def main():
    """
    Main entry point for the application.

    Initializes the virtual reality environment, loads patient data, and starts a new therapy session.
    """
    try:
        # Initialize the virtual reality environment
        vr_environment = virtual_reality_environment.VirtualRealityEnvironment()
        vr_environment.initialize()

        # Load patient data
        patient_data_loader = patient_data.PatientDataLoader()
        patient_data = patient_data_loader.load_patient_data()

        # Start a new therapy session
        therapy_session_manager = therapy_session.TherapySessionManager(vr_environment, patient_data)
        therapy_session_manager.start_session()

    except Exception as e:
        # Log any uncaught exceptions
        logging.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()