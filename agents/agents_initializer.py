import json
import os
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, ChatCompletion, config_list_openai_aoai
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import chromadb

import tempfile
from tools.git_repo_scrapper import git_repo_scraper
from tools.query_knowledge_graph import query_knowledge_graph
from utils.observer import Observable

from utils.poly_logger import PolyLogger
from llms_config import LlmConfiguration
from tools.planner import task_planner
from tools.scrape_website import scrape_website
from tools.search import search
from tools.summary import summary
from utils.mongo_db import AgentDB
from utils.workspace import Workspace

# Create a temporary directory
temp_dir = tempfile.mkdtemp()

LOG = PolyLogger(__name__)

# Get current file directory
current_file_dir = os.path.dirname(os.path.abspath(__file__))

# Load JSON relative to this file location
func_json_file_path = os.path.join(
    current_file_dir, 'FUNCTIONS_DESCRIPTIONS.json')

with open(func_json_file_path) as f:
    FUNCTIONS_DESCRIPTIONS = json.load(f)


class AgentInitializer(Observable):
    def __init__(self, database: AgentDB, workspace: Workspace):
        super().__init__()  # Initialize Observable

        self.database = database
        self.workspace = workspace

        self._agents = {}
        self._groupchat = None
        self._manager = None
        self.agent_helpers = []
        self.setup_agent()

    # Properties for controlled access
    @property
    def agents(self):
        return self._agents

    @property
    def groupchat(self):
        return self._groupchat

    @property
    def manager(self):
        return self._manager

    def setup_agent(self):

        # Configuration setup
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

        def termination_msg(x): return isinstance(
            x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

        self.set_llm_config = {
            "request_timeout": 600,
            "seed": 42,
            "config_list": config_list_instance.config,
            "temperature": 0,
        }

        self.admin_assistant = UserProxyAgent(
            name="Admin_Assistant",
            is_termination_msg=termination_msg,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            code_execution_config={
                "work_dir": "tools",
            },
            function_map={
                "task_planner": task_planner,
                "search": search,
                "scrape_website": scrape_website,
                "summary": summary,
                "git_repo_scraper":git_repo_scraper, 
                "query_knowledge_graph": query_knowledge_graph
            },
        )

        self.engineer = AssistantAgent(
            name="Engineer",
            llm_config={
                "temperature": 0,
                "request_timeout": 600,
                "seed": 42,
                "model": "gpt-4-0613",
                "config_list": config_list_openai_aoai(exclude="aoai"),
                "functions": FUNCTIONS_DESCRIPTIONS
            }            
        )

        self._agents = {
            "admin_assistant": self.admin_assistant,
            "engineer": self.engineer,

        }

        self._groupchat = GroupChat(
            agents=[
                self.admin_assistant,
                self.engineer,
            ],
            messages=[],
            max_round=50
        )

        self._manager = GroupChatManager(
            groupchat=self.groupchat,
            llm_config=self.set_llm_config
        )

        ChatCompletion.start_logging()
        LOG.info("Start logging...")

    def initiate_chat(self, user_input):
        LOG.info(
            f"Entering {self.__class__.__name__}.initiate_chat() with user_input: {user_input}")

        self.admin_assistant.initiate_chat(
            self.manager,
            message=user_input
        )

        LOG.info(f"Exiting {self.__class__.__name__}.initiate_chat()")
