# Copyright 2023 Dre Proprietary
#
# This software is provided by the copyright holders and contributors "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. In no event shall the copyright holder or contributors be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.

import logging
from typing import List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def parse_input_data(data: str) -> dict:
    """
    Parses input data string into a dictionary.
    
    Args:
        data (str): Input data string containing key-value pairs separated by commas.
        
    Returns:
        dict: Parsed data as a dictionary.
    """
    parsed_data = {}
    try:
        for item in data.split(','):
            key, value = item.strip().split(':')
            parsed_data[key.strip()] = value.strip()
    except ValueError as e:
        logger.error(f"Failed to parse input data: {e}")
        raise
    return parsed_data

def process_data(data_dict: dict) -> List[str]:
    """
    Processes the parsed data and returns a list of processed strings.
    
    Args:
        data_dict (dict): Parsed data as a dictionary.
        
    Returns:
        List[str]: Processed data as a list of strings.
    """
    processed_list = []
    try:
        for key, value in data_dict.items():
            if 'micro' in key.lower() and 'sas' in value.lower():
                processed_list.append(f"Processed: {key} -> {value}")
    except Exception as e:
        logger.error(f"Failed to process data: {e}")
        raise
    return processed_list

def ava_optimized_1916(input_data: str) -> List[str]:
    """
    Main function for the micro-SaaS productivity utility.
    
    Args:
        input_data (str): Input data string containing key-value pairs separated by commas.
        
    Returns:
        List[str]: Processed data as a list of strings.
    """
    try:
        parsed_data = parse_input_data(input_data)
        result = process_data(parsed_data)
        return result
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

# Example usage
if __name__ == "__main__":
    input_data = "micro1:sas1,micro2:sas2,micro3:sas3"
    try:
        output = ava_optimized_1916(input_data)
        for item in output:
            print(item)
    except Exception as e:
        logger.error(f"Failed to run example: {e}")