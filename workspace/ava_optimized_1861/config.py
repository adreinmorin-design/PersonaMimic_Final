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

logger = logging.getLogger(__name__)

class Config:
    """
    Configuration settings for the ava_optimized_1861 SaaS project.
    """

    def __init__(self):
        self.logging_level = "DEBUG"
        self.database_url = "sqlite:///ava_optimized_1861.db"
        self.api_key = "your_api_key_here"
        self.jwt_secret = "your_jwt_secret_here"
        self.allowed_hosts = ["localhost", "0.0.0.0"]
        self.microlearning_timeout = 300
        self.healthcheck_interval = 60

    def setup_logging(self):
        """
        Set up logging configuration.
        """
        try:
            logging.basicConfig(level=self.logging_level)
            logger.info("Logging configured successfully.")
        except Exception as e:
            logger.error(f"Failed to configure logging: {e}")

    def validate_config(self):
        """
        Validate the configuration settings.
        """
        if not self.api_key or not self.jwt_secret:
            raise ValueError("API key and JWT secret must be set.")

config = Config()
config.setup_logging()

# Example usage
if __name__ == "__main__":
    config.validate_config()