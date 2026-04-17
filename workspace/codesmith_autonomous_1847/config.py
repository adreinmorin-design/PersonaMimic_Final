# Copyright 2023 Dre Proprietary
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Config:
    """
    Configuration settings for the codesmith_autonomous_1847 SaaS project.
    """

    def __init__(self):
        self.logging_level = logging.INFO
        self.database_url = "sqlite:///micro_learning.db"
        self.api_key = "your_api_key_here"
        self.jwt_secret = "your_jwt_secret_here"
        self.allowed_origins = ["http://localhost:3000", "https://client.example.com"]
        self.micro_learning_duration = 15
        self.learning_sessions_per_day = 4
        self.max_concurrent_users = 100
        self.email_from_address = "noreply@codesmith-autonomous.com"
        self.smtp_server = "smtp.yourserver.com"
        self.smtp_port = 587
        self.smtp_username = "your_smtp_username"
        self.smtp_password = "your_smtp_password"

    def validate(self):
        """
        Validate the configuration settings.

        Raises:
            ValueError: If any required setting is missing or invalid.
        """
        if not self.api_key:
            raise ValueError("API key must be set.")
        if not self.jwt_secret:
            raise ValueError("JWT secret must be set.")
        if not self.database_url:
            raise ValueError("Database URL must be set.")
        if not all([self.smtp_server, self.smtp_port, self.smtp_username, self.smtp_password]):
            raise ValueError("SMTP settings are incomplete.")

    def log_config(self):
        """
        Log the configuration details.
        """
        logging.info(f"Logging Level: {self.logging_level}")
        logging.info(f"Database URL: {self.database_url}")
        logging.info(f"API Key: {'*' * len(self.api_key)}")
        logging.info(f"JWT Secret: {'*' * len(self.jwt_secret)}")
        logging.info(f"Allowed Origins: {self.allowed_origins}")
        logging.info(f"Micro Learning Duration (minutes): {self.micro_learning_duration}")
        logging.info(f"Learning Sessions per Day: {self.learning_sessions_per_day}")
        logging.info(f"Max Concurrent Users: {self.max_concurrent_users}")
        logging.info(f"Email From Address: {self.email_from_address}")
        logging.info(f"SMTP Server: {self.smtp_server}")
        logging.info(f"SMTP Port: {self.smtp_port}")

config = Config()

try:
    config.validate()
    config.log_config()
except ValueError as e:
    logging.error(e)