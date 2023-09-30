from flaml import autogen
from flaml.autogen.retrieve_utils import create_vector_db_from_dir, query_vector_db, get_file_from_url, get_files_from_dir
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import chromadb

# Configuration for GPT-4
config_list = autogen.config_list_from_json(
    "../OAI_CONFIG_LIST.json",
    filter_dict={
        "model": ["gpt-4-0613", "gpt-4-32k", "gpt-4", "gpt-4-0314", "gpt-3.5-turbo", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613", "gpt-35-turbo-16k"],
    },
)

model_config = {
    "seed": 42,
    "temperature": 0,
    "config_list": config_list,
    "request_timeout": 1200,
}

# Common working directory for relevant agents
working_directory = "software_project_files"

# the purpose of the following line is to log the conversation history
autogen.ChatCompletion.start_logging()

# DevManager
dev_manager = autogen.UserProxyAgent(
    name="DevManager",
    system_message="DevManager: Define requirements, design the architecture, and review code. Collaborate with the team for deploying and refining the software. Remember to stay in character.",
    code_execution_config={
        "work_dir": working_directory,
        "use_docker": False,  # set to True or image name like "python:3" to use docker
        "timeout": 120,
        "last_n_messages": 1,
    },
)

# AgentRetrieverAssistant is responsible for assising the AgentRetriever with any task
agent_retriever_assistant = RetrieveAssistantAgent(
    name="AgentRetrieverAssistant",
    system_message="You assist the AgentRetriever solve the task presented until the task is completed successfully",
    llm_config={
        "request_timeout": 600,
        "seed": 42,
        "config_list": config_list,
    },
)

MAX_TOKENS = 2048  # OpenAI's max token limit
# AgentRetriever is responsible for retrieving documents or files
agent_retriever = RetrieveUserProxyAgent(
    name="AgentRetriever",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    retrieve_config={
        # The task of the retrieve chat. Possible values are "code", "qa", and "default".
        "task": "default",
        # Path to the docs directory. Can also be a path to a single file or the URL to a single file.
        "docs_path": working_directory,
        # The chunk token size for the retrieve chat.
        "chunk_token_size": 2000,
        # The model to use for the retrieve chat.
        "model": config_list[0]["model"],
        # The chromadb client.
        "client": chromadb.PersistentClient(path="/tmp/chromadb"),
        # The embedding model to use for the retrieve chat.
        "embedding_model": "all-mpnet-base-v2",
        # Name of the collection. Default is "autogen-docs".
        "collection_name": "autogen-docs",
        # Context max token size for the retrieve chat.
        # "context_max_tokens": int(MAX_TOKENS * 0.8),
        # Chunk mode for the retrieve chat. Possible values: "multi_lines" and "one_line".
        # "chunk_mode": "multi_lines",
        # Chunk will only break at an empty line if True. Ignored if chunk_mode is "one_line".
        # "must_break_at_empty_line": True,
        # Customized prompt for the retrieve chat. Default is None.
        # "customized_prompt": None,
    },
)

# Executor-Tester
executor_tester = autogen.UserProxyAgent(
    name="Executor-Tester",
    system_message="Executor-Tester: Execute and test the developed software. Report outcomes and possible issues. Remember to stay in character.",
    code_execution_config={
        "work_dir": working_directory,
        "use_docker": False,  # set to True or image name like "python:3" to use docker
        "timeout": 120,
        "last_n_messages": 1,
    },
    human_input_mode="ALWAYS",
)

# WebSurfer
web_surfer = autogen.UserProxyAgent(
    name="WebSurfer",
    system_message="WebSurfer: Fetch online resources, best practices, or any other relevant information. Remember to stay in character. Reply TERMINATE if the task has been solved at full satisfaction. Otherwise, reply CONTINUE, or the reason why the task is not solved yet. Reply TERMINATE if the task has been solved at full satisfaction. Otherwise, reply CONTINUE, or the reason why the task is not solved yet.",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get(
        "content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "web"},
    llm_config=model_config,
)

# FileManager with local file interactions
file_manager = autogen.UserProxyAgent(
    name="FileManager",
    system_message="FileManager: Manage files, save code, retrieve past versions, and organize the workspace. Saves all focumentation. Remember to stay in character.",
    code_execution_config={
        "work_dir": working_directory,
        "use_docker": False,  # set to True or image name like "python:3" to use docker
        "timeout": 120,
        "last_n_messages": 1,
    },
    human_input_mode="NEVER",
)

# Code Reviewer - AssistantAgent
code_reviewer = autogen.AssistantAgent(
    name="CodeReviewer",
    llm_config=model_config,
    system_message="Code Reviewer: Your role is to inspect the provided code meticulously. Ensure that it meets the standards of quality, efficiency, and follows best coding practices. Provide feedback and recommend any necessary enhancements or changes. Always stay in character during interactions."
)

# Programmer - AssistantAgent
programmer = autogen.AssistantAgent(
    name="Programmer",
    llm_config=model_config,
    system_message="Programmer: Your responsibility is to develop the required code to fulfill the given task. Ensure to save your code in the designated working directory. Utilize a virtual environment (venv) for managing dependencies and consistently update the 'requirements.txt' file. Always stay in character during interactions."
)

# Systems Engineer - AssistantAgent
systems_engineer = autogen.AssistantAgent(
    name="SystemsEngineer",
    llm_config=model_config,
    system_message="Systems Engineer: Your main task is to design the system architecture for the software project in focus. Document all the intricate details and save them in a dedicated document. Collaborate with other agents to ensure a comprehensive and cohesive design. Always stay in character during interactions."
)

# Scribe - AssistantAgent
scribe = autogen.AssistantAgent(
    name="Scribe",
    llm_config=model_config,
    system_message="Scribe: Your role is to diligently write documentation and notes. Ensure that all important details, decisions, and changes are documented and saved in an organized manner. Always stay in character during interactions."
)


# Group Chat Setup
groupchat = autogen.GroupChat(
    agents=[
        "dev_manager",
        "agent_retriever_assistant",
        "agent_retriever",
        "executor_tester",
        "web_surfer",
        "file_manager",
        "code_reviewer",
        "programmer",
        "systems_engineer",
        "scribe"
    ],
    messages=[],
    max_round=150  # Increased max_round for extended interaction
)
manager = autogen.GroupChatManager(
    groupchat=groupchat, llm_config=model_config)

# Initiating Chat
dev_manager.initiate_chat(
    manager,
    message="We have a new project that we are about to start developing and I would like everyone to respond with their name and role in the project. Once everyone has introduced themselves then I will tell you about the project"
)
