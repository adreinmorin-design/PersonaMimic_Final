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
    Configuration settings for the fenko_autonomous_1845 SaaS project.
    """

    def __init__(self):
        self.database_url = "sqlite:///fenko.db"
        self.api_key = "your_api_key_here"
        self.logging_level = logging.INFO
        self.enable_debug_mode = False

    def get_database_url(self) -> str:
        """
        Get the database URL configuration.
        """
        return self.database_url

    def set_database_url(self, url: str):
        """
        Set the database URL configuration.

        :param url: The new database URL.
        """
        self.database_url = url
        logging.info(f"Database URL updated to {url}")

    def get_api_key(self) -> str:
        """
        Get the API key configuration.
        """
        return self.api_key

    def set_api_key(self, api_key: str):
        """
        Set the API key configuration.

        :param api_key: The new API key.
        """
        self.api_key = api_key
        logging.info(f"API Key updated to {api_key}")

    def get_logging_level(self) -> int:
        """
        Get the logging level configuration.
        """
        return self.logging_level

    def set_logging_level(self, level: int):
        """
        Set the logging level configuration.

        :param level: The new logging level (e.g., logging.DEBUG, logging.INFO).
        """
        self.logging_level = level
        logging.info(f"Logging level updated to {level}")

    def enable_debug_mode(self) -> bool:
        """
        Get the debug mode status.
        """
        return self.enable_debug_mode

    def toggle_debug_mode(self):
        """
        Toggle the debug mode configuration.

        :return: The new state of debug mode (True or False).
        """
        self.enable_debug_mode = not self.enable_debug_mode
        logging.info(f"Debug mode toggled to {self.enable_debug_mode}")
        return self.enable_debug_mode

# Example usage:
config = Config()
logging.info(config.get_database_url())
config.set_database_url("sqlite:///new_fenko.db")
logging.info(config.get_api_key())
config.set_api_key("new_api_key_here")
logging.info(config.get_logging_level())
config.set_logging_level(logging.DEBUG)
logging.info(config.enable_debug_mode())
config.toggle_debug_mode()