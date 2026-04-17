# Copyright 2023 Dre Proprietary
# All rights reserved.

"""
main.py

This module serves as the entry point for our SaaS project 'dre_autonomous_1892'.
It initializes the application, sets up logging, and starts the main application loop.
"""

import logging
from dre_autonomous_1892.core import CoreApplication
from dre_autonomous_1892.utils.config_loader import load_config

# Set up logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("dre_autonomous.log"),
                              logging.StreamHandler()])

def main():
    """
    Main function to initialize and run the application.
    """
    try:
        # Load configuration settings
        config = load_config()
        
        # Initialize the core application with loaded configurations
        app = CoreApplication(config)
        
        # Start the application loop
        app.run()
    
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()