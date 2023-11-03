#RAG.py
import os
import chromadb

from autogen.oai.openai_utils import config_list_from_json
from autogen.retrieve_utils import TEXT_FORMATS
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.oai.completion import ChatCompletion


def setup_configurations():
    """Setup configurations for the agent."""
    config_list = config_list_from_json(
        "../OAI_CONFIG_LIST.json",
        filter_dict={
            "model": [
                "gpt-4-32k",
                "gpt-35-turbo-16k",
            ]
        },
    )

    assert len(config_list) > 0
    print("models to use: ", [config_list[i]["model"]
          for i in range(len(config_list))])
    print("Accepted file formats for `docs_path`:")
    print(TEXT_FORMATS)
    print(config_list)
    return config_list


def initialize_agents(config_list):
    """Initialize agents for RetrieveChat."""
    ChatCompletion.start_logging()

    assistant = RetrieveAssistantAgent(
        name="assistant",
        system_message='''Engineer. You follow an approved plan. You write python/shell code to solve tasks. 
            Wrap the code in a code block that specifies the script type. The user can't modify your code.
            So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
            Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
            If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. 
            If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
        ''',
        llm_config={
            "request_timeout": 3600,
            "seed": 42,
            "config_list": config_list,
        },
    )

    ragproxyagent = RetrieveUserProxyAgent(
        name="ragproxyagent",
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=10,
        retrieve_config={
            "task": "code",
            "docs_path": "C:\\Users\\Shadow\\Documents\\Repo\\PolyGPT\\project_docs",
            "chunk_token_size": 2000,
            "model": config_list[0]["model"],
            "collection_name": "test",
            "client": chromadb.PersistentClient(path="/tmp/chromadb"),
            "embedding_model": "all-mpnet-base-v2",
            "get_or_create": True,
        },
    )

    return assistant, ragproxyagent


def chat_with_agent(assistant, ragproxyagent):
    """Chat with the agent through terminal."""
    assistant.reset()
    print("Welcome to the chat agent. Enter your problem or type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        ragproxyagent.initiate_chat(assistant, problem=user_input)


if __name__ == "__main__":
    config_list = setup_configurations()
    assistant, ragproxyagent = initialize_agents(config_list)
    chat_with_agent(assistant, ragproxyagent)