# Dre Proprietary
# Copyright (c) 2023 Dre Autonomous 1868. All rights reserved.
# This software is the confidential and proprietary information of Dre Autonomous 1868.
# ("Confidential Information"). You shall not disclose such Confidential Information and shall use it only in accordance with the terms of the license agreement you entered into with Dre Autonomous 1868.

"""
Main entry point for the dre_autonomous_1868 SaaS project.

This module provides the primary interface for the Personalized Micro-Learning tool for Remote Healthcare Professionals.
It utilizes Domain-Driven Design (DDD) principles to ensure a modular, maintainable, and scalable architecture.
"""

import logging
import sys
from dre_autonomous_1868.domain import healthcare_professional
from dre_autonomous_1868.domain import micro_learning_module
from dre_autonomous_1868.infrastructure import database
from dre_autonomous_1868.infrastructure import logger

# Initialize the logger
logger.init_logger()

def main():
    """
    Main entry point for the application.

    This function orchestrates the primary workflow of the application, including:
    1. Initializing the database connection
    2. Loading healthcare professional data
    3. Loading micro-learning module data
    4. Providing personalized micro-learning recommendations
    """
    try:
        # Initialize the database connection
        db_connection = database.init_db_connection()
        
        # Load healthcare professional data
        healthcare_professionals = healthcare_professional.load_healthcare_professionals(db_connection)
        
        # Load micro-learning module data
        micro_learning_modules = micro_learning_module.load_micro_learning_modules(db_connection)
        
        # Provide personalized micro-learning recommendations
        for professional in healthcare_professionals:
            recommended_modules = micro_learning_module.get_recommended_modules(professional, micro_learning_modules)
            logger.log_info(f"Recommended micro-learning modules for {professional.name}: {recommended_modules}")
        
    except Exception as e:
        logger.log_error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()