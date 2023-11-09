import json
import os
from poly_logger import PolyLogger, LogLevel  # Ensure this path matches where your PolyLogger is located

# Initialize logger
logger = PolyLogger(__name__)

def load_json(filename):
    """
    Load a JSON file from the 'json' directory located at the project root.
    
    Args:
    - filename (str): The name of the JSON file to load.
    
    Returns:
    - dict: The content of the JSON file as a dictionary.
    
    Raises:
    - FileNotFoundError: If the JSON file does not exist.
    - json.JSONDecodeError: If the JSON file cannot be parsed.
    - Exception: For other unforeseen errors during file reading.
    
    Usage:
    - config_data = load_json('my_config.json')
    """
    # Establish the base path by finding the project root
    base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    # Define the standard path to the 'json' directory
    json_path = os.path.join(base_path, 'json')
    # Create the full file path
    file_path = os.path.join(json_path, filename)

    # Try to open and load the JSON file
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            logger.log(LogLevel.INFO, f"Successfully loaded {filename}")
            return data
    except FileNotFoundError:
        logger.log(LogLevel.ERROR, f"The file {file_path} was not found.")
        raise
    except json.JSONDecodeError:
        logger.log(LogLevel.ERROR, f"The file {file_path} is not a valid JSON file.")
        raise
    except Exception as e:
        logger.log(LogLevel.CRITICAL, f"An error occurred while loading {file_path}: {e}")
        raise

# Example usage
# This assumes that 'my_config.json' is in the 'json' directory at the project root
# try:
#     config_data = load_json('my_config.json')
#     # Further processing with config_data...
# except Exception as e:
#     # Handle exception or log as necessary
#     # Exception is already logged by the logger within the function
#     pass
