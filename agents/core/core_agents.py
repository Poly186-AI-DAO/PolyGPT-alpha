from autogen import AssistantAgent, UserProxyAgent, config_list_openai_aoai, GroupChat, GroupChatManager
import os
import json
import logging

from agents.specialized_agents.internet_agent import internet_agent
from agents.specialized_agents.planner_agent import planner_agent

from agents.teams.research_team import research_team

from llms_config import LlmConfiguration

# Initializing the logger
logging.basicConfig(level=logging.INFO)

class CoreAgent:
    def __init__(self):

        # Instantiate the LlmConfiguration with filtering
        llm_filters = [
            "gpt-4-32k",
            "gpt-35-turbo-16k",
            "gpt4",
            "gpt-4-0314",
            "gpt-4-0613",
            "gpt-4-32k-0314",
            "gpt-4-32k-v0314"
        ]
        config_list_instance = LlmConfiguration(filter_llms=llm_filters)
        
        self.llm_config = {
            "request_timeout": 600,
            "seed": 42,
            "config_list": config_list_instance.config, # Accessing the 'config' attribute of our instance
            "temperature": 0,
        }

        self.script_dir = os.path.dirname(os.path.realpath(__file__))

        # Initialize agents
        self.userAgent = self._initialize_userAgent()
        self.teamsCoordinator = self._initialize_teamsCoordinator()
        self.librarianAgent = self._initialize_librarianAgent()
        self.coreAssistant = self._initialize_coreAssistant()

    def _load_json(self, relative_path):
        """Loads a JSON from a given relative path."""
        absolute_path = os.path.join(self.script_dir, relative_path)
        with open(absolute_path, 'r') as f:
            return json.load(f)

    def _initialize_userAgent(self):
        """Initialize the UserAgent."""
        logging.info("Initializing UserAgent...")
                
        specialized_agent_map = {
            "internet_agent": internet_agent,
            "planner_agent": planner_agent
        }
        
        agent = UserProxyAgent(
            name="UserAgent",
            human_input_mode="TERMINATE",
            function_map=specialized_agent_map
        )
        logging.info("UserAgent initialized.")
        return agent

    def _initialize_teamsCoordinator(self):
        """Initialize the TeamsCoordinator."""
        logging.info("Initializing TeamsCoordinator...")
        
        teams_map = {
            "research_team": research_team,
        }
        
        agent = UserProxyAgent(
            name="TeamsCoordinator",
            human_input_mode="TERMINATE",
            function_map=teams_map
        )
        logging.info("TeamsCoordinator initialized.")
        return agent

    def _initialize_librarianAgent(self):
        """Initialize the LibrarianAgent."""
        logging.info("Initializing LibrarianAgent...")
                
        librarian_map = {
            # Assuming some function mappings here, e.g., "store_data": store_function
        }
        
        agent = UserProxyAgent(
            name="LibrarianAgent",
            human_input_mode="TERMINATE",
            function_map=librarian_map
        )
        logging.info("LibrarianAgent initialized.")
        return agent

    def _initialize_coreAssistant(self):
        """Initialize the CoreAssistant."""
        logging.info("Initializing CoreAssistant...")
        
        specialized_agents_json = self._load_json('../../utils/specialized_agents.json')
        
        agent = AssistantAgent(
            name="CoreAssistant",
            llm_config={
                "temperature": 1,
                "request_timeout": 600,
                "seed": 42,
                "model": "gpt-4-0613",
                "config_list": config_list_openai_aoai(exclude="aoai"),
                "functions": specialized_agents_json
            }
        )
        logging.info("CoreAssistant initialized.")
        return agent

    def initiate_chat(self, message):
        # Initiate a group chat with all agents
        logging.info("Initiating group chat...")
        
        groupchat = GroupChat(
            agents=[self.userAgent, self.teamsCoordinator, self.librarianAgent, self.coreAssistant],
            messages=[],
            max_round=50
        )
        
        manager = GroupChatManager(groupchat=groupchat, llm_config=self.llm_config)
        
        self.userAgent.initiate_chat(manager, message=message)

        logging.info("Chat initiated.")
