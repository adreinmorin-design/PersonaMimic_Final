# Dre Proprietary
# Copyright (c) 2023 YourCompany Inc.

import datetime

def get_current_timestamp():
    """
    This function returns the current timestamp in ISO format.

    Returns:
        str: The current timestamp as a string in ISO format.
    """
    try:
        # Get the current timestamp
        current_time = datetime.datetime.now()
        
        # Format the timestamp to ISO 8601 format
        iso_timestamp = current_time.isoformat(timespec='milliseconds')
        
        return iso_timestamp
    except Exception as e:
        # Log the error with a traceback for debugging purposes
        import logging
        logging.error(f"Error occurred while getting current timestamp: {e}", exc_info=True)
        raise

# Example usage (optional, can be removed if not needed in this module)
if __name__ == "__main__":
    print(get_current_timestamp())