# Dre Proprietary
# Copyright (c) 2023 Dre Optimized 1275

import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_template_data(data):
    """
    Processes the template data and returns a formatted result.
    
    :param data: A dictionary containing template data.
    :return: Processed and formatted template data.
    """
    try:
        # Example processing logic
        processed_data = {
            'template_id': data.get('id'),
            'name': data.get('name', 'Unknown'),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        logging.info(f"Processed template: {processed_data}")
        return processed_data
    except Exception as e:
        logging.error(f"Error processing template data: {e}")
        raise

def validate_template(template):
    """
    Validates the given template against predefined rules.
    
    :param template: A dictionary representing a template.
    :return: True if valid, False otherwise.
    """
    try:
        required_fields = ['id', 'name']
        missing_fields = [field for field in required_fields if field not in template]
        
        if missing_fields:
            logging.warning(f"Template is invalid due to missing fields: {missing_fields}")
            return False
        
        # Additional validation logic
        if len(template['name']) < 3:
            logging.warning("Template name is too short.")
            return False
        
        return True
    except Exception as e:
        logging.error(f"Error validating template: {e}")
        raise

def main():
    """
    Main function to orchestrate the workflow.
    """
    try:
        # Example input data
        template_data = {
            'id': 12345,
            'name': 'Example Template'
        }
        
        if validate_template(template_data):
            processed_data = process_template_data(template_data)
            logging.info(f"Processed and validated template: {processed_data}")
    except Exception as e:
        logging.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main()