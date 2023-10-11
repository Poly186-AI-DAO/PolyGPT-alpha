# 1. Imports
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

    return config_list


def initialize_agents(config_list):
    """Initialize agents for RetrieveChat."""
    ChatCompletion.start_logging()

    assistant = RetrieveAssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant.",
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