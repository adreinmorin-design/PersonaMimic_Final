# Dre Proprietary
# Copyright (c) 2023, Ava Autonomous
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import logging
import os
from pathlib import Path
from typing import Dict, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_dir = self.base_dir / 'config'
        self.data_dir = self.base_dir / 'data'
        self.models_dir = self.base_dir / 'models'
        self.log_dir = self.base_dir / 'logs'

    def load_config(self) -> Dict:
        """
        Load configuration from file.
        """
        config_file = self.config_dir / 'config.json'
        try:
            with open(config_file, 'r') as f:
                config = self._parse_json(f.read())
                logger.info('Loaded configuration from file.')
                return config
        except FileNotFoundError:
            logger.error('Configuration file not found.')
            return {}
        except Exception as e:
            logger.error(f'Error loading configuration: {e}')
            return {}

    def _parse_json(self, json_str: str) -> Dict:
        """
        Parse JSON string into a dictionary.
        """
        try:
            return self._json.loads(json_str)
        except Exception as e:
            logger.error(f'Error parsing JSON: {e}')
            return {}

    def get_config(self) -> Dict:
        """
        Get the current configuration.
        """
        config = self.load_config()
        if not config:
            logger.error('No configuration loaded.')
            return {}
        return config

    def save_config(self, config: Dict) -> None:
        """
        Save configuration to file.
        """
        config_file = self.config_dir / 'config.json'
        try:
            with open(config_file, 'w') as f:
                self._json.dump(config, f, indent=4)
                logger.info('Saved configuration to file.')
        except Exception as e:
            logger.error(f'Error saving configuration: {e}')

    def get_model_config(self, model_name: str) -> Dict:
        """
        Get the configuration for a specific model.
        """
        model_config_file = self.models_dir / f'{model_name}.json'
        try:
            with open(model_config_file, 'r') as f:
                return self._parse_json(f.read())
        except FileNotFoundError:
            logger.error(f'Model configuration file not found for {model_name}.')
            return {}
        except Exception as e:
            logger.error(f'Error loading model configuration: {e}')
            return {}

    def save_model_config(self, model_name: str, config: Dict) -> None:
        """
        Save the configuration for a specific model.
        """
        model_config_file = self.models_dir / f'{model_name}.json'
        try:
            with open(model_config_file, 'w') as f:
                self._json.dump(config, f, indent=4)
                logger.info(f'Saved model configuration to file for {model_name}.')
        except Exception as e:
            logger.error(f'Error saving model configuration: {e}')

    def get_data_config(self) -> Dict:
        """
        Get the configuration for data storage and retrieval.
        """
        data_config_file = self.data_dir / 'config.json'
        try:
            with open(data_config_file, 'r') as f:
                return self._parse_json(f.read())
        except FileNotFoundError:
            logger.error('Data configuration file not found.')
            return {}
        except Exception as e:
            logger.error(f'Error loading data configuration: {e}')
            return {}

    def save_data_config(self, config: Dict) -> None:
        """
        Save the configuration for data storage and retrieval.
        """
        data_config_file = self.data_dir / 'config.json'
        try:
            with open(data_config_file, 'w') as f:
                self._json.dump(config, f, indent=4)
                logger.info('Saved data configuration to file.')
        except Exception as e:
            logger.error(f'Error saving data configuration: {e}')

    def get_log_config(self) -> Dict:
        """
        Get the configuration for logging.
        """
        log_config_file = self.log_dir / 'config.json'
        try:
            with open(log_config_file, 'r') as f:
                return self._parse_json(f.read())
        except FileNotFoundError:
            logger.error('Log configuration file not found.')
            return {}
        except Exception as e:
            logger.error(f'Error loading log configuration: {e}')
            return {}

    def save_log_config(self, config: Dict) -> None:
        """
        Save the configuration for logging.
        """
        log_config_file = self.log_dir / 'config.json'
        try:
            with open(log_config_file, 'w') as f:
                self._json.dump(config, f, indent=4)
                logger.info('Saved log configuration to file.')
        except Exception as e:
            logger.error(f'Error saving log configuration: {e}')

    def get_base_config(self) -> Dict:
        """
        Get the base configuration.
        """
        return {
            'base_dir': str(self.base_dir),
            'config_dir': str(self.config_dir),
            'data_dir': str(self.data_dir),
            'models_dir': str(self.models_dir),
            'log_dir': str(self.log_dir),
        }

    def save_base_config(self, config: Dict) -> None:
        """
        Save the base configuration.
        """
        base_config_file = self.base_dir / 'base_config.json'
        try:
            with open(base_config_file, 'w') as f:
                self._json.dump(config, f, indent=4)
                logger.info('Saved base configuration to file.')
        except Exception as e:
            logger.error(f'Error saving base configuration: {e}')

# Import the required JSON library
import json as _json