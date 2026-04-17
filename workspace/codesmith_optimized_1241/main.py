# Copyright 2023 Dre Proprietary
# All rights reserved.

import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(file_path):
    """
    Load data from a file into memory.
    
    :param file_path: Path to the data file.
    :return: List of dictionaries containing the parsed data.
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        headers = lines[0].strip().split(',')
        data = [dict(zip(headers, line.strip().split(','))) for line in lines[1:]]
        return data
    except Exception as e:
        logging.error(f"Error loading data from {file_path}: {e}")
        raise

def filter_data(data, filters):
    """
    Filter the loaded data based on provided filters.
    
    :param data: List of dictionaries containing the parsed data.
    :param filters: Dictionary of filters to apply.
    :return: Filtered list of dictionaries.
    """
    try:
        filtered_data = [record for record in data if all(record.get(key) == value for key, value in filters.items())]
        return filtered_data
    except Exception as e:
        logging.error(f"Error filtering data: {e}")
        raise

def aggregate_data(data, aggregation_key):
    """
    Aggregate the data based on a specific key.
    
    :param data: List of dictionaries containing the parsed data.
    :param aggregation_key: Key to aggregate the data by.
    :return: Aggregated data as a dictionary.
    """
    try:
        aggregated = {}
        for record in data:
            key_value = record.get(aggregation_key)
            if key_value not in aggregated:
                aggregated[key_value] = 0
            aggregated[key_value] += 1
        return aggregated
    except Exception as e:
        logging.error(f"Error aggregating data: {e}")
        raise

def generate_report(data, report_type):
    """
    Generate a report based on the type requested.
    
    :param data: List of dictionaries containing the parsed data.
    :param report_type: Type of report to generate (e.g., 'summary', 'detail').
    :return: Report content as a string.
    """
    try:
        if report_type == 'summary':
            filtered_data = filter_data(data, {'status': 'active'})
            aggregated_data = aggregate_data(filtered_data, 'category')
            report_content = "Summary Report:\n"
            for key, value in aggregated_data.items():
                report_content += f"{key}: {value}\n"
        elif report_type == 'detail':
            filtered_data = filter_data(data, {'status': 'active'})
            report_content = "Detail Report:\n"
            for record in filtered_data:
                report_content += f"Record: {record}\n"
        else:
            raise ValueError("Unsupported report type")
        
        return report_content
    except Exception as e:
        logging.error(f"Error generating report: {e}")
        raise

def main():
    """
    Main function to orchestrate the data processing and reporting.
    """
    try:
        file_path = 'data.csv'
        data = load_data(file_path)
        
        filters = {'status': 'active'}
        filtered_data = filter_data(data, filters)
        
        aggregation_key = 'category'
        aggregated_data = aggregate_data(filtered_data, aggregation_key)
        
        report_type = 'summary'
        report_content = generate_report(data, report_type)
        
        logging.info(f"Report generated: {report_content}")
    except Exception as e:
        logging.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main()