# Dre Proprietary
# Copyright (c) 2023 Dre. All rights reserved.
# This software is the confidential and proprietary information of Dre.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you entered into with Dre.

import os
import sys
from setuptools import setup, find_packages

# Define the package metadata
NAME = 'codesmith_autonomous_1847'
VERSION = '1.0.0'
DESCRIPTION = 'High-performance tool for Personalized Micro-Learning for Remote Healthcare Professionals'
AUTHOR = 'Dre'
AUTHOR_EMAIL = 'info@dre.com'
LICENSE = 'Proprietary'

# Define the package requirements
INSTALL_REQUIRES = [
    'numpy',
    'pandas',
    'scikit-learn',
    'tensorflow',
    'keras',
    'flask',
    'sqlalchemy',
    'psycopg2',
    'requests',
    'logging'
]

# Define the package entry points
ENTRY_POINTS = {
    'console_scripts': [
        'codesmith_autonomous_1847 = codesmith_autonomous_1847.main:main'
    ]
}

def read_file(filename):
    """
    Reads the contents of a file.

    Args:
        filename (str): The name of the file to read.

    Returns:
        str: The contents of the file.
    """
    try:
        with open(filename, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return ""

def write_file(filename, contents):
    """
    Writes the contents to a file.

    Args:
        filename (str): The name of the file to write.
        contents (str): The contents to write to the file.
    """
    try:
        with open(filename, 'w') as file:
            file.write(contents)
    except Exception as e:
        print(f"Error writing file: {e}")

def setup_package():
    """
    Sets up the package.
    """
    try:
        setup(
            name=NAME,
            version=VERSION,
            description=DESCRIPTION,
            author=AUTHOR,
            author_email=AUTHOR_EMAIL,
            license=LICENSE,
            packages=find_packages(),
            install_requires=INSTALL_REQUIRES,
            entry_points=ENTRY_POINTS,
            long_description=read_file('README.md'),
            long_description_content_type='text/markdown'
        )
    except Exception as e:
        print(f"Error setting up package: {e}")

if __name__ == '__main__':
    setup_package()