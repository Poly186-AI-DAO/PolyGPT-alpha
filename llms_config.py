import os
from autogen.oai.openai_utils import config_list_from_json

class LlmConfiguration:
    _instance = None
    _is_initialized = False
    
    def __new__(cls, filter_llms=None):
        if not cls._instance:
            cls._instance = super(LlmConfiguration, cls).__new__(cls)
        return cls._instance

    def __init__(self, filter_llms=None):
        # Ensure that the initialization happens only once
        if LlmConfiguration._is_initialized:
            return

        file_name = "OAI_CONFIG_LIST.json"
        filter_dict = None

        # If filter_llms is provided, use it for filtering
        if filter_llms:
            filter_dict = {"model": filter_llms}

        self.config = self._find_and_load_config(file_name, filter_dict)
        LlmConfiguration._is_initialized = True

    def _find_and_load_config(self, file_name, filter_dict):
        # Search for the file starting from the current directory and moving to parent directories
        current_dir = os.path.abspath(os.getcwd())
        while current_dir != os.path.dirname(current_dir):  # To prevent infinite loop on root dir
            file_path = os.path.join(current_dir, file_name)
            if os.path.exists(file_path):
                return config_list_from_json(env_or_file=file_name, file_location=current_dir, filter_dict=filter_dict)
            # Move to parent directory
            current_dir = os.path.dirname(current_dir)
        raise FileNotFoundError(f"'{file_name}' not found in any parent directories.")

    def __getitem__(self, key):
        return self.config[key]
