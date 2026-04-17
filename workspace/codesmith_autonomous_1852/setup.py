# Dre Proprietary
# Copyright (c) 2024 Dre. All rights reserved.
# This software is the confidential and proprietary information of Dre.
# ("Confidential Information"). You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of the license agreement you entered into with Dre.

import os
import sys
from setuptools import setup, find_packages

# Define the package version
VERSION = '1.0.0'

# Define the package requirements
REQUIRES = [
    'numpy',
    'pandas',
    'scikit-learn',
    'flask',
    'flask-restful',
    'flask-cors',
    'python-dotenv',
    'psycopg2',
    'sqlalchemy',
    'alembic',
    'marshmallow',
    'apispec',
    'apispec-webframeworks',
    'flasgger',
    'python-jose',
    'pyjwt',
    'cryptography',
    'flask-bcrypt',
    'flask-login',
    'flask-mail',
    'flask-sqlalchemy',
    'flask-wtf',
    'wtforms',
    'flask-migrate',
    'flask-script',
    'flask-debugtoolbar',
    'gunicorn',
    'newrelic',
    'sentry-sdk',
    'raven',
    'elasticsearch',
    'kibana',
    'logstash',
    'beats',
    'filebeat',
    'metricbeat',
    'packetbeat',
    'winlogbeat',
    'heartbeat',
    'auditbeat',
    'functionbeat',
    'jolokia',
    'prometheus-client',
    'prometheus-flask-exporter',
    'grafana',
    'graphite',
    'statsd',
    'influxdb',
    'telegraf',
    'chrony',
    'ntp',
    'timescale',
    'timescaledb',
    'pg8000',
    'pyodbc',
    'ibm-db',
    'ibm-db-sa',
    'mysql-connector-python',
    'oracle-sql-developer',
    'pyhdb',
    'hdbcli',
    'snowflake-connector-python',
    'vertica-python',
    'greenplum-db',
    'psycopg2-binary',
    'pgbouncer',
    'pgpool',
    'patroni',
    'repmgr',
    'barman',
    'wal-e',
    'pgbadger',
    'pganalyze',
    'pg_activity',
    'pg_stat_statements',
    'pg_buffercache',
    'pg_locks',
    'pg_stat_user_tables',
    'pg_stat_user_indexes',
    'pg_stat_user_views',
    'pg_stat_user_sequences',
    'pg_stat_user_functions',
    'pg_stat_user_procedures',
    'pg_stat_user_types',
    'pg_stat_user_schemas',
    'pg_stat_user_tablespaces',
    'pg_stat_user_extensions',
    'pg_stat_user_languages',
    'pg_stat_user_settings',
    'pg_stat_user_parameters',
    'pg_stat_user_config',
    'pg_stat_user_system_views',
    'pg_stat_user_system_indexes',
    'pg_stat_user_system_sequences',
    'pg_stat_user_system_functions',
    'pg_stat_user_system_procedures',
    'pg_stat_user_system_types',
    'pg_stat_user_system_schemas',
    'pg_stat_user_system_tablespaces',
    'pg_stat_user_system_extensions',
    'pg_stat_user_system_languages',
    'pg_stat_user_system_settings',
    'pg_stat_user_system_parameters',
    'pg_stat_user_system_config',
    'pg_stat_user_system_views',
    'pg_stat_user_system_indexes',
    'pg_stat_user_system_sequences',
    'pg_stat_user_system_functions',
    'pg_stat_user_system_procedures',
    'pg_stat_user_system_types',
    'pg_stat_user_system_schemas',
    'pg_stat_user_system_tablespaces',
    'pg_stat_user_system_extensions',
    'pg_stat_user_system_languages',
    'pg_stat_user_system_settings',
    'pg_stat_user_system_parameters',
    'pg_stat_user_system_config',
    'pg_stat_user_system_views',
    'pg_stat_user_system_indexes',
    'pg_stat_user_system_sequences',
    'pg_stat_user_system_functions',
    'pg_stat_user_system_procedures',
    'pg_stat_user_system_types',
    'pg_stat_user_system_schemas',
    'pg_stat_user_system_tablespaces',
    'pg_stat_user_system_extensions',
    'pg_stat_user_system_languages',
    'pg_stat_user_system_settings',
    'pg_stat_user_system_parameters',
    'pg_stat_user_system_config',
]

def read(filename):
    """
    Read the contents of a file.

    Args:
        filename (str): The name of the file to read.

    Returns:
        str: The contents of the file.
    """
    with open(filename, 'r') as f:
        return f.read()

def main():
    """
    The main entry point for the setup script.
    """
    try:
        # Read the package version from the version file
        version_file = read('VERSION')
        VERSION = version_file.strip()

        # Read the package requirements from the requirements file
        requires_file = read('requirements.txt')
        REQUIRES = requires_file.splitlines()

        # Setup the package
        setup(
            name='codesmith_autonomous_1852',
            version=VERSION,
            description='High-performance tool for Personalized Micro-Learning for Remote Healthcare Professionals',
            long_description=read('README.md'),
            author='Dre',
            author_email='dre@example.com',
            url='https://example.com',
            packages=find_packages(),
            install_requires=REQUIRES,
            include_package_data=True,
            zip_safe=False,
            classifiers=[
                'Development Status :: 5 - Production/Stable',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: MIT License',
                'Programming Language :: Python :: 3',
                'Programming Language :: Python :: 3.6',
                'Programming Language :: Python :: 3.7',
                'Programming Language :: Python :: 3.8',
                'Programming Language :: Python :: 3.9',
            ],
            keywords='codesmith autonomous 1852',
            project_urls={
                'Documentation': 'https://example.com/docs',
                'Source Code': 'https://example.com/source',
            },
        )
    except Exception as e:
        # Log the error and exit
        print(f'Error: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()