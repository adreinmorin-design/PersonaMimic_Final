# Dre Proprietary
# Copyright (c) 2023 Dre Inc.

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def validate_input(data: dict) -> bool:
    """
    Validates the input data for further processing.
    
    Args:
        data (dict): Input data to be validated.
        
    Returns:
        bool: True if validation passes, False otherwise.
    """
    required_keys = {'id', 'name', 'value'}
    return set(data.keys()) >= required_keys

def process_data(data_list: List[Dict[str, any]]) -> Dict[str, int]:
    """
    Processes the input data list and returns a summary.
    
    Args:
        data_list (List[Dict[str, any]]): List of dictionaries containing data to be processed.
        
    Returns:
        Dict[str, int]: Summary dictionary with counts of different types of data.
    """
    summary = {'total': 0, 'valid': 0}
    for data in data_list:
        if validate_input(data):
            summary['valid'] += 1
        summary['total'] += 1
    return summary

def audit_data(data: List[Dict[str, any]]) -> Dict[str, int]:
    """
    Audits the provided data to ensure it meets the required criteria.
    
    Args:
        data (List[Dict[str, any]]): Data list to be audited.
        
    Returns:
        Dict[str, int]: Audit summary with counts of valid and total entries.
    """
    try:
        if not isinstance(data, list):
            raise ValueError("Input must be a list.")
        audit_summary = process_data(data)
        return audit_summary
    except Exception as e:
        logger.error(f"An error occurred during data auditing: {e}")
        raise

def main():
    sample_data = [
        {'id': 1, 'name': 'Alice', 'value': 100},
        {'id': 2, 'name': 'Bob'},
        {'id': 3, 'name': 'Charlie', 'value': 200}
    ]
    
    try:
        result = audit_data(sample_data)
        print("Audit Summary:", result)
    except Exception as e:
        logger.error(f"Failed to execute main function: {e}")

if __name__ == "__main__":
    main()