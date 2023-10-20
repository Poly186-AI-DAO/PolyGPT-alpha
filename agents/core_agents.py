import logging
from autogen import AssistantAgent, UserProxyAgent, config_list_openai_aoai

import os
import json
from agents.internet_agent import internet_agent

from agents.planner_agent import planner_agent
from agents.research_team import research_team
from utils.orchestrator import ConversationType
from utils.orchestrator import Orchestrator



class CoreAgent:
    def __init__(self):
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.realpath(__file__))

        specialized_agent_json_path = os.path.join(
            script_dir, '../utils/specialized_agents.json')

        # Build the path to agent_teams.json from the script's directory
        agent_teams_path = os.path.join(
            script_dir, '../utils/agent_teams.json')

        # Load the function tools
        with open(specialized_agent_json_path, 'r') as f:
            specialized_agents_json = json.load(f)

        # Load the function tools
        with open(agent_teams_path, 'r') as f:
            agent_teams_json = json.load(f)

        # Map the function names from the JSON to their respective imported functions
        specialized_agent_map = {
            "planner_agent": planner_agent,
            "internet_agent": internet_agent
        }

        # Map the function names from the JSON to their respective imported functions
        agent_teams_map = {
            "research_team": research_team,
        }

        # Create the agent_caller
        self.poly_core = UserProxyAgent(
            name="Poly Core",
            human_input_mode="ALWAYS",
            max_consecutive_auto_reply=10,
            code_execution_config={"work_dir": "../../tools"},
            function_map=specialized_agent_map
        )

        # Assistant agent
        self.poly_core_assistant = AssistantAgent(
            name="Poly Core Assistant",
            llm_config={
                "temperature": 1,
                "request_timeout": 600,
                "seed": 42,
                "model": "gpt-4-0613",
                "config_list": config_list_openai_aoai(exclude="aoai"),
                "functions": specialized_agents_json
            },
        )

    def initiate_chat(self, message):
        # Initiate a group chat based on the Orchestrator's defined patterns
        logging.info("Initiating group chat...")
        
        agents = [self.poly_core, self.poly_core_assistant]
        orchestrator = Orchestrator(name="MainOrchestrator", agents=agents)
        
        orchestrator.start_conversation(
            pattern=ConversationType.ALL_TO_ALL,
            initial_message=message,
            starter_name=self.poly_core.name,
            agent_order_names=[
                self.poly_core.name, 
                self.poly_core_assistant.name
            ]
        )

        logging.info("Chat initiated.")
