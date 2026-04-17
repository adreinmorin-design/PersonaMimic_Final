# Dre Proprietary
# Copyright (c) 2023 Dre. All rights reserved.
# This software is the confidential and proprietary information of Dre.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you entered into with Dre.

import os
import sys
from setuptools import setup, find_packages

# Define the package metadata
NAME = 'fenko_autonomous_1845'
VERSION = '1.0.0'
DESCRIPTION = 'High-performance tool for Micro-SaaS Productivity Utilities'
AUTHOR = 'Dre'
AUTHOR_EMAIL = 'dre@example.com'
LICENSE = 'Proprietary'

# Define the package dependencies
INSTALL_REQUIRES = [
    'numpy>=1.20.0',
    'pandas>=1.3.5',
    'matplotlib>=3.5.1',
    'scikit-learn>=1.0.2',
    'loguru>=0.5.3'
]

# Define the package entry points
ENTRY_POINTS = {
    'console_scripts': [
        'fenko_autonomous_1845=fenko_autonomous_1845.cli:main'
    ]
}

def read_file(filename):
    """
    Read the contents of a file.

    Args:
        filename (str): The name of the file to read.

    Returns:
        str: The contents of the file.
    """
    try:
        with open(filename, 'r') as file:
            return file.read()
    except Exception as e:
        import loguru
        logger = loguru.logger
        logger.error(f'Failed to read file: {filename}')
        logger.error(str(e))
        sys.exit(1)

def main():
    """
    The main entry point for the setup script.
    """
    try:
        # Read the package metadata from the README file
        readme = read_file('README.md')
        changelog = read_file('CHANGELOG.md')

        # Define the package long description
        long_description = readme + '\n\n' + changelog

        # Setup the package
        setup(
            name=NAME,
            version=VERSION,
            description=DESCRIPTION,
            long_description=long_description,
            long_description_content_type='text/markdown',
            author=AUTHOR,
            author_email=AUTHOR_EMAIL,
            license=LICENSE,
            packages=find_packages(),
            install_requires=INSTALL_REQUIRES,
            entry_points=ENTRY_POINTS,
            classifiers=[
                'Development Status :: 5 - Production/Stable',
                'Intended Audience :: Developers',
                'License :: Other/Proprietary License',
                'Programming Language :: Python :: 3.8',
                'Programming Language :: Python :: 3.9',
                'Programming Language :: Python :: 3.10'
            ]
        )
    except Exception as e:
        import loguru
        logger = loguru.logger
        logger.error('Failed to setup package')
        logger.error(str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()