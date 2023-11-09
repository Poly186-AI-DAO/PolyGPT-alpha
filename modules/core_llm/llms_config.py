import json
from utils.json_loader import load_json
from utils.poly_logger import PolyLogger, LogLevel

# Initialize logger
logger = PolyLogger(__name__)

class LlmConfiguration:
    _instance = None
    _is_initialized = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LlmConfiguration, cls).__new__(cls)
        return cls._instance

    def __init__(self, filter_llms=None):
        # Ensure that the initialization happens only once
        if LlmConfiguration._is_initialized:
            return

        file_name = "OAI_CONFIG_LIST.json"

        try:
            # Load the configuration using the provided load_json function
            config_data = load_json(file_name)
            
            # Log the type and value of filter_llms
            logger.log(LogLevel.DEBUG, f"filter_llms type: {type(filter_llms)}")
            logger.log(LogLevel.DEBUG, f"filter_llms content: {filter_llms}")

            # If filter_llms is provided and is a string, filter the configurations
            if isinstance(filter_llms, str):
                self.config = [model_config for model_config in config_data if filter_llms in model_config.get("model", "")]
            elif isinstance(filter_llms, list):
                # If filter_llms is a list, check if any of the filter items are in the model name
                self.config = [model_config for model_config in config_data if any(filter_item in model_config.get("model", "") for filter_item in filter_llms)]
            else:
                self.config = config_data
            
            logger.log(LogLevel.INFO, "LlmConfiguration initialized successfully.")
        except Exception as e:
            logger.log(LogLevel.CRITICAL, f"An error occurred while initializing LlmConfiguration: {e}")
            raise

        LlmConfiguration._is_initialized = True

    def __getitem__(self, index):
        return self.config[index]

    def get_model_config(self, model_name):
        # Return the configuration for the specified model
        for model_config in self.config:
            if model_name in model_config.get("model", ""):
                return model_config
        return None
