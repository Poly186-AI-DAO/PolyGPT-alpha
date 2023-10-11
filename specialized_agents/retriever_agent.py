# 1. Imports
import os
import time
import chromadb
import logging
import autogen
from autogen.oai.openai_utils import config_list_from_json
from autogen.retrieve_utils import (
    split_files_to_chunks,
    get_files_from_dir,
    create_vector_db_from_dir,
    query_vector_db,
    TEXT_FORMATS
)
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.oai.completion import ChatCompletion

# Global Configuration
CONFIG = {
    "model": "text-embedding-ada-002",
    "api_key": "ed91b45a11f046bbad4dcc2cc21275b3",
    "api_base": "https://poly.openai.azure.com/openai/deployments/poly/chat/completions",
    "api_type": "azure",
    "api_version": "2"
}

# TODO: Remove or replace hardcoded paths and configurations
DOCS_PATH = "C:\\Users\\Shadow\\Documents\\Repo\\PolyGPT\\project_docs"
MAX_HEARTBEAT_CHECKS = 5  # Adjust this number based on your requirements
CHROMADB = "/tmp/chromadb" 

# Functions
def setup_configurations():
    """Setup configurations for the agent."""
    # TODO: Verify the configuration file path and adjust if necessary
    config_list = config_list_from_json(
        "../OAI_CONFIG_LIST.json",
        filter_dict={
            "model": [
                "gpt-4-32k",
                "gpt-35-turbo-16k",
            ]
        },
    )
    assert len(config_list) > 0, "No models found in the configuration list."
    print("models to use: ", [config_list[i]["model"] for i in range(len(config_list))])
    print("Accepted file formats for `docs_path`:")
    print(TEXT_FORMATS)

    return config_list

def initialize_agents(config_list):
    """Initialize agents for RetrieveChat."""
    ChatCompletion.start_logging()
    assistant = RetrieveAssistantAgent(
        # TODO: Verify and adjust configuration parameters if necessary
        name="assistant",
        system_message="You are a helpful assistant.",
        llm_config={
            "request_timeout": 3600,
            "seed": 42,
            "config_list": config_list,
        },
    )
    assert os.path.isdir(DOCS_PATH), f"Directory {DOCS_PATH} does not exist."
    ragproxyagent = RetrieveUserProxyAgent(
        # TODO: Verify and adjust configuration parameters if necessary
        name="ragproxyagent",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=2,
        retrieve_config={
            "docs_path": DOCS_PATH,
            "chunk_token_size": 2000,
            "model": config_list[0]["model"],
            "collection_name": "project_docs",
            "client": chromadb.PersistentClient(path=CHROMADB),
            "embedding_model": "all-mpnet-base-v2",
            "update_context": True,
        },
    )

    return assistant, ragproxyagent

def embed_documents_in_db(client):
    """Embed documents from a directory into ChromaDB."""
    # TODO: Adjust embedding parameters if necessary
    create_vector_db_from_dir(
        dir_path=DOCS_PATH,
        client=client,
        collection_name="project_docs",
        get_or_create=True
    )

def chat_with_agent(assistant, ragproxyagent):
    """Chat with the agent through terminal."""
    assistant.reset()
    print("Welcome to the chat agent. Enter your problem or type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        ragproxyagent.initiate_chat(assistant, problem=user_input)

def process_and_query_documents(client):
    """Process and query documents stored in ChromaDB."""
    # TODO: Adjust processing and querying parameters if necessary
    files_list = get_files_from_dir(dir_path=DOCS_PATH)
    chunks = split_files_to_chunks(files=files_list)
    create_vector_db_from_dir(
        dir_path=DOCS_PATH,
        client=client,
        collection_name="project_docs",
        get_or_create=True,
        embedding_model="all-mpnet-base-v2",
        db_path=CHROMADB
    )
    query_result = query_vector_db(
        n_results=10,
        db_path=CHROMADB,
        search_string="",
        query_texts=["what is Poly186 ?"],
        client=client,
        collection_name="project_docs",
        embedding_model="all-mpnet-base-v2",
    )

    return query_result

def test_embeddings(embeddings, collection_name):
    """Test embeddings against the provided collection in ChromaDB."""
    # TODO: Adjust test parameters if necessary
    client = chromadb.PersistentClient(path="/path/to/data")
    collection = client.get_or_create_collection(collection_name)
    query_results = collection.query(
        query_embeddings=[embeddings],
        n_results=5
    )
    for idx, result in enumerate(query_results['ids']):
        print(f"Result {idx + 1}:")
        print(f"ID: {result}")
        print(f"Document: {query_results['documents'][idx]}")
        print(f"Metadata: {query_results['metadatas'][idx]}")
        print(f"Distance: {query_results['distances'][idx]}")
        print("-" * 40)

if __name__ == "__main__":
    # Setup
    logging.basicConfig(level=logging.DEBUG)
    config_list = setup_configurations()
    assert os.path.isdir(DOCS_PATH), f"Directory {DOCS_PATH} does not exist."
    client = chromadb.PersistentClient(path=CHROMADB)

    # Connect to ChromaDB
    for _ in range(MAX_HEARTBEAT_CHECKS):
        heartbeat = client.heartbeat()
        print("ChromaDB Client Heartbeat: ", heartbeat)
        time.sleep(5)

    # Embed and Query Documents
    embed_documents_in_db(client)
    query_result = process_and_query_documents(client)
    print("Query Result:", query_result)

    # Chat with Agent
    assistant, ragproxyagent = initialize_agents(config_list)
    chat_with_agent(assistant, ragproxyagent)

    # Test Embeddings
    sample_embedding = [1.1, 2.3, 3.2]
    test_embeddings(sample_embedding, "project_docs")
