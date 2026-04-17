# Dre Proprietary
# Copyright (c) 2024 Masterbrain Autonomous. All rights reserved.

"""
Main entry point for Masterbrain Autonomous 1869.
"""

import logging
import sys
from typing import Dict, List
from masterbrain_autonomous_1869.core import config, services
from masterbrain_autonomous_1869.core.domain import models
from masterbrain_autonomous_1869.core.infrastructure import repositories, use_cases

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

def main() -> None:
    """
    Main entry point for Masterbrain Autonomous 1869.
    """
    try:
        # Load configuration
        config.load()

        # Initialize services
        services.init()

        # Initialize repositories
        repositories.init()

        # Initialize use cases
        use_cases.init()

        # Run application
        run_application()

    except Exception as e:
        # Log and exit on error
        logging.error(f"Error: {e}")
        sys.exit(1)


def run_application() -> None:
    """
    Run the application.
    """
    # Get user input
    user_input: str = input("Enter a command: ")

    # Parse user input
    command: str = user_input.split()[0]

    # Handle command
    if command == "create":
        create_user()
    elif command == "list":
        list_users()
    elif command == "delete":
        delete_user()
    else:
        logging.info("Unknown command. Type 'help' for available commands.")


def create_user() -> None:
    """
    Create a new user.
    """
    # Get user details
    name: str = input("Enter user name: ")
    email: str = input("Enter user email: ")

    # Create user
    user: models.User = models.User(name=name, email=email)
    use_cases.create_user(user=user)

    # Log success
    logging.info(f"User created: {user.name}")


def list_users() -> None:
    """
    List all users.
    """
    # Get users
    users: List[models.User] = use_cases.get_users()

    # Log users
    for user in users:
        logging.info(f"User: {user.name} ({user.email})")


def delete_user() -> None:
    """
    Delete a user.
    """
    # Get user name
    name: str = input("Enter user name: ")

    # Delete user
    use_cases.delete_user(name=name)

    # Log success
    logging.info(f"User deleted: {name}")


if __name__ == "__main__":
    main()