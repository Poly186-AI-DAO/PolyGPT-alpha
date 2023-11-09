import json
import os
import tempfile
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, ChatCompletion
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import chromadb
from modules.core_llm.llms_config import LlmConfiguration
from modules.tools.planner import task_planner
from modules.tools.search import search
from utils.json_loader import load_json

from utils.poly_observer import PolyObservable
from utils.poly_logger import PolyLogger


# Create a temporary directory
temp_dir = tempfile.mkdtemp()

LOG = PolyLogger(__name__)

# Load the JSON data using the load_json function
FUNCTIONS_DESCRIPTIONS = load_json('FUNCTIONS_DESCRIPTIONS.json')


class AgentInitializer(PolyObservable):
    def __init__(self):
        super().__init__()  # Initialize Observable


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
            human_input_mode="ALWAYS",
            system_message="The boss who ask questions and give tasks. Retrieve concent when there is need for more information from the documentation ",
        )

        self.boss_aid = RetrieveUserProxyAgent(
            name="Boss_Assistant",
            is_termination_msg=termination_msg,
            system_message="""Assistant who has extra content retrieval power for solving difficult problems.
            As a Librarian who has extra content retrieval power for solving difficult problems.
            You are the primary interface between the user and the Retriever_Assistant.
            Direct the Retriever_Assistant to accomplish tasks.
            Only terminate the task when you're fully satisfied or if the user indicates so.
            If not satisfied, provide a clear reason for the dissatisfaction or reply CONTINUE to keep the task ongoing.
            Ensure the user is aware they can reply TERMINATE if the task has been solved to full satisfaction.
            """,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
            retrieve_config={
                "task": "qa",
                "docs_path": "C:\\Users\\Shadow\\Documents\\Repo\\PolyGPT\\project_docs",
                "chunk_token_size": 2000,
                "model": config_list_instance.config[3]["model"],
                "collection_name": "poly_docs",
                "client": chromadb.PersistentClient(path="/tmp/chromadb"),
                "embedding_model": "all-mpnet-base-v2",
                "get_or_create": True,
            },
            code_execution_config=False,
        )

        self.coder = AssistantAgent(
            name="Senior_Python_Engineer",
            is_termination_msg=termination_msg,
            system_message="""You are a senior python engineer. To write the best code, Retrieve concent when there is need for more information from the documentation 
            Engineer. You follow an approved plan. You write python/shell code to solve tasks. 
            Wrap the code in a code block that specifies the script type. The user can't modify your code.
            So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
            Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
            If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. 
            If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
            """,
            llm_config=self.set_llm_config,
        )

        self.pm = AssistantAgent(
            name="Product_Manager",
            is_termination_msg=termination_msg,
            system_message="You are a product manager. for the best plan retrieve content needed based on the request.  ",
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
            # "scrape_website": scrape_website,
            # "summary": summary,
            # "git_repo_scraper": git_repo_scraper,
            # "query_knowledge_graph": query_knowledge_graph
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