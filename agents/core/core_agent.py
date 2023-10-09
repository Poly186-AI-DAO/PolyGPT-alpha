from autogen import AssistantAgent, UserProxyAgent, config_list_openai_aoai

import os
import json

# Import the functions from their file locations
from specialized_agents.internet_agent import use_internet_agent
from specialized_agents.planner_agent import initiate_planner_chat


class CoreAgent:
    def __init__(self):
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.realpath(__file__))

        # Build the path to function_tools.json from the script's directory
        function_tools_path = os.path.join(
            script_dir, '../../utils/function_tools.json')

        # Build the path to agent_teams.json from the script's directory
        agent_teams_path = os.path.join(
            script_dir, '../../utils/agent_teams.json')

        # Load the function tools
        with open(function_tools_path, 'r') as f:
            function_tools_json = json.load(f)

        # Load the function tools
        with open(agent_teams_path, 'r') as f:
            agent_teams_json = json.load(f)

        # Map the function names from the JSON to their respective imported functions
        function_map = {
            "initiate_planner_chat": initiate_planner_chat,
            "use_internet_agent": use_internet_agent
        }

        # Create the agent_caller
        self.poly_core = UserProxyAgent(
            name="Poly Core",
            human_input_mode="TERMINATE",
            max_consecutive_auto_reply=10,
            code_execution_config={"work_dir": "generated_functions"},
            function_map=function_map
        )

        # Create the mind_stem AssistantAgent
        self.poly_core_assistant = AssistantAgent(
            name="Poly Core Assistant",
            llm_config={
                "temperature": 0,
                "request_timeout": 600,
                "seed": 42,
                "model": "gpt-4-0613",
                "config_list": config_list_openai_aoai(exclude="aoai"),
                "functions": function_tools_json
            }
        )

    def initiate_chat(self, message):
        # Initiate a chat with the mind_stem using the agent_caller
        self.poly_core.initiate_chat(
            self.poly_core_assistant,
            message=message
        )
