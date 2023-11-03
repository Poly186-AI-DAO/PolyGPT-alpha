import json
import os
import tempfile
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, ChatCompletion
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from utils.observer import Observable
from utils.poly_logger import PolyLogger
from llms_config import LlmConfiguration
from tools.git_repo_scrapper import git_repo_scraper
from tools.query_knowledge_graph import query_knowledge_graph
from tools.planner import task_planner
from tools.scrape_website import scrape_website
from tools.search import search
from tools.summary import summary
from utils.mongo_db import AgentDB
from utils.workspace import Workspace
import chromadb

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
        # Configuration setup (keep it as it is from your original code)
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
        LOG.info(
            f"config_list_instance: {config_list_instance} + config_list_instance.config: {config_list_instance.config}")
        
        def termination_msg(x): return isinstance(
            x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

        self.set_llm_config = {
            "functions": FUNCTIONS_DESCRIPTIONS,
            "request_timeout": 600,
            "seed": 42,
            "config_list": config_list_instance.config,
            "temperature": 0,
        }

        # Agents from the example (using your config setup)
        self.boss = UserProxyAgent(
            name="Boss",
            is_termination_msg=termination_msg,
            human_input_mode="TERMINATE",
            system_message="The boss who ask questions and give tasks.",
        )

        self.boss_aid = RetrieveUserProxyAgent(
            name="Boss_Assistant",
            is_termination_msg=termination_msg,
            system_message="Assistant who has extra content retrieval power for solving difficult problems.",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
            retrieve_config={
                "task": "code",
                "docs_path": "C:\\Users\\Shadow\\Documents\\Repo\\PolyGPT\\project_docs",
                "chunk_token_size": 2000,
                "model": config_list_instance.config[0]["model"],
                "collection_name": "test",
                "client": chromadb.PersistentClient(path="/tmp/chromadb"),
                "embedding_model": "all-mpnet-base-v2",
                "get_or_create": True,
            },
            code_execution_config=False,
        )

        self.coder = AssistantAgent(
            name="Senior_Python_Engineer",
            is_termination_msg=termination_msg,
            system_message="You are a senior python engineer. ",
            llm_config=self.set_llm_config,
        )

        self.pm = AssistantAgent(
            name="Product_Manager",
            is_termination_msg=termination_msg,
            system_message="You are a product manager. ",
            llm_config=self.set_llm_config,
        )

        self.reviewer = AssistantAgent(
            name="Code_Reviewer",
            is_termination_msg=termination_msg,
            system_message="You are a code reviewer. ",
            llm_config=self.set_llm_config,
        )

        # Function to retrieve content based on the example provided
        def retrieve_content(message, n_results=3):
            self.boss_aid.n_results = n_results  # Set the number of results to be retrieved.
            # Check if we need to update the context.
            update_context_case1, update_context_case2 = self.boss_aid._check_update_context(message)
            if (update_context_case1 or update_context_case2) and self.boss_aid.update_context:
                self.boss_aid.problem = message if not hasattr(self.boss_aid, "problem") else self.boss_aid.problem
                _, ret_msg = self.boss_aid._generate_retrieve_user_reply(message)
            else:
                ret_msg = self.boss_aid.generate_init_message(message, n_results=n_results)
            return ret_msg if ret_msg else message

        # Register functions for all agents
        common_function_map = {
            "retrieve_content": retrieve_content,
            "task_planner": task_planner,
            "search": search,
            "scrape_website": scrape_website,
            "summary": summary,
            "git_repo_scraper": git_repo_scraper,
            "query_knowledge_graph": query_knowledge_graph
        }

        for agent in [self.boss, self.coder, self.pm, self.reviewer]:
            agent.register_function(function_map=common_function_map)

        # GroupChat and GroupChatManager setup
        self._groupchat = GroupChat(
            agents=[self.boss, self.coder, self.pm, self.reviewer],
            messages=[],
            max_round=12
        )

        self._manager = GroupChatManager(
            groupchat=self.groupchat,
            llm_config=self.set_llm_config
        )

        ChatCompletion.start_logging()
        LOG.info("Start logging...")

            
    def initiate_chat(self, user_input):
            # Log the user input
            LOG.info(f"Entering {self.__class__.__name__}.initiate_chat() with user_input: {user_input}")

            # Here we initiate chat with the 'boss' agent as in the provided example
            # Replace 'self.boss' with 'boss' if 'boss' is not a class attribute but a local variable
            self.boss.initiate_chat(
                self._manager,  # Assuming self._manager is the GroupChatManager instance
                message=user_input
            )

            # Log the exit from the initiate_chat method
            LOG.info(f"Exiting {self.__class__.__name__}.initiate_chat()")