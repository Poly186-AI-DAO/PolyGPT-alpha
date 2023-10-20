import os
import chromadb

from autogen.oai.openai_utils import config_list_from_json
from autogen.retrieve_utils import TEXT_FORMATS
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent


def retriever_agent(message: str, docs_path: str, collection_name: str):
    """
    Communicate with the Retriever Agent Assistant to fetch information from provided documents.
    :param message: Task or question for the retriever.
    :param docs_path: Path to the directory containing documents.
    :param collection_name: Name of the collection for the retriever.
    :return: None
    """
    # Setup configurations for the agent.
    config_list = config_list_from_json(
        env_or_file="OAI_CONFIG_LIST.json",
        file_location="C:\\Users\\Shadow\\Documents\\Repo\PolyGPT\\",
        filter_dict={
            "model": [
                "gpt-4-32k",
                "gpt-35-turbo-16k",
            ]
        },
    )

    assert len(config_list) > 0
    print("Accepted file formats for `docs_path`:")
    print(TEXT_FORMATS)

    # Initialize the Retriever Assistant Agent.
    retriever_assistant = RetrieveAssistantAgent(
        name="Retriever_Assistant",
        system_message='''You are designed to extract information from provided documents.
        When given a task or query, search the specified document collection and return the relevant details.
        Ensure the returned information is concise and pertinent to the query.
        ''',
        llm_config={
            "request_timeout": 3600,
            "seed": 42,
            "config_list": config_list,
        },
    )

    # Initialize the UserProxyAgent for the retriever.
    retriever_user_proxy = RetrieveUserProxyAgent(
        name="Retriever_User_Proxy",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=10,
        retrieve_config={
            "task": "code",
            "docs_path": docs_path,
            "chunk_token_size": 2000,
            "model": config_list[0]["model"],
            "collection_name": collection_name,
            "client": chromadb.PersistentClient(path="/tmp/chromadb"),
            "embedding_model": "all-mpnet-base-v2",
            "get_or_create": True,
        },
        system_message='''You are the primary interface between the user and the Retriever_Assistant. 
        Direct the Retriever_Assistant to accomplish tasks.
        Only terminate the task when you're fully satisfied or if the user indicates so. 
        If not satisfied, provide a clear reason for the dissatisfaction or reply CONTINUE to keep the task ongoing. 
        Ensure the user is aware they can reply TERMINATE if the task has been solved to full satisfaction.
        '''
    )

    # Initiate a chat with the Retriever Assistant using the provided message.
    retriever_user_proxy.initiate_chat(
        retriever_assistant,
        message=message
    )
