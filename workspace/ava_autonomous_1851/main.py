# Dre Proprietary
# Copyright (c) 2023 Dre. All rights reserved.
# This software is the confidential and proprietary information of Dre.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you entered into with Dre.

"""
Main entry point for the ava_autonomous_1851 SaaS project.

This module provides the primary interface for the personalized, AI-driven, and adaptive mental wellness coaching tool.
It utilizes Domain-Driven Design (DDD) principles to ensure a clean, modular, and maintainable architecture.
"""

import logging
from logging.config import dictConfig
import os
from ava_autonomous_1851.domain import CoachingSession, User
from ava_autonomous_1851.infrastructure import CoachingSessionRepository, UserRepository
from ava_autonomous_1851.application import CoachingService

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

    This function initializes the necessary components and starts the coaching session.
    """
    try:
        # Initialize the user repository
        user_repository = UserRepository()

        # Initialize the coaching session repository
        coaching_session_repository = CoachingSessionRepository()

        # Initialize the coaching service
        coaching_service = CoachingService(user_repository, coaching_session_repository)

        # Create a new user
        user = User(
            id=os.environ.get('USER_ID'),
            name=os.environ.get('USER_NAME'),
            email=os.environ.get('USER_EMAIL')
        )

        # Create a new coaching session
        coaching_session = CoachingSession(
            id=os.environ.get('COACHING_SESSION_ID'),
            user_id=user.id,
            start_time=os.environ.get('COACHING_SESSION_START_TIME')
        )

        # Start the coaching session
        coaching_service.start_coaching_session(coaching_session)

        # Log the coaching session
        logging.info(f'Coaching session {coaching_session.id} started for user {user.id}')

    except Exception as e:
        # Log the error
        logging.error(f'An error occurred: {e}')

if __name__ == '__main__':
    main()