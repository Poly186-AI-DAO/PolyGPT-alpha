import json
import os

from utils.poly_logger import LogLevel, PolyLogger

# Initialize logger
logger = PolyLogger(__name__)

def find_json_file(start_dir, filename):
    """
    Recursively search for a JSON file starting from the given directory.

    Args:
    - start_dir (str): The starting directory for the search.
    - filename (str): The name of the JSON file to find.

    Returns:
    - str: The path to the JSON file if found, otherwise None.
    """
    for root, dirs, files in os.walk(start_dir):
        if filename in files:
            return os.path.join(root, filename)
    return None

def load_json(filename):
    """
    Load a JSON file by searching the entire project directory.
    
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

    # Search for the JSON file in the project directory
    file_path = find_json_file(base_path, filename)
    if not file_path:
        logger.log(LogLevel.ERROR, f"The file {filename} was not found in the project.")
        raise FileNotFoundError(f"The file {filename} was not found in the project.")

    # Try to open and load the JSON file
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            logger.log(LogLevel.INFO, f"Successfully loaded {filename}")
            return data
    except json.JSONDecodeError:
        logger.log(LogLevel.ERROR, f"The file {file_path} is not a valid JSON file.")
        raise
    except Exception as e:
        logger.log(LogLevel.CRITICAL, f"An error occurred while loading {file_path}: {e}")
        raise

# Example usage
# This will search the entire project directory for 'my_config.json'
# try:
#     config_data = load_json('my_config.json')
#     # Further processing with config_data...
# except Exception as e:
#     # Handle exception or log as necessary
#     # Exception is already logged by the logger within the function
#     pass
