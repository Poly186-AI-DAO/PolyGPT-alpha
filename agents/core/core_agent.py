import os
import json
from flaml import autogen
from functions.internet_agent import use_internet_agent
from functions.planner_agent import initiate_planner_chat

class CoreAgent:
    def __init__(self):
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.realpath(__file__))

        # Build the path to function_tools.json from the script's directory
        function_tools_path = os.path.join(script_dir, '../../utils/function_tools.json')

        # Load the function tools
        with open(function_tools_path, 'r') as f:
            function_tools = json.load(f)

        # Create the agent_caller
        self.poly_core = autogen.UserProxyAgent(
            name="Poly Core",
            human_input_mode="TERMINATE",
            max_consecutive_auto_reply=10,
            code_execution_config={"work_dir": "interactions"},
            function_map=function_tools
        )

        # Create the mind_stem AssistantAgent
        self.poly_core_assistant = autogen.AssistantAgent(
            name="Poly Core Assistant",
            llm_config={
                "temperature": 0,
                "request_timeout": 600,
                "seed": 42,
                "model": "gpt-4-0613",
                "config_list": autogen.config_list_openai_aoai(exclude="aoai"),
                "functions": function_tools
            }
        )

    def initiate_chat(self, message):
        # Initiate a chat with the mind_stem using the agent_caller
        self.poly_core.initiate_chat(
            self.poly_core_assistant, 
            message=message
        )