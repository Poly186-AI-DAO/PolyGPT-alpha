
import autogen
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import chromadb
import json
import os

# Initial Setup
# Structuring the code into functions

def initial_setup():
    # Initial setup: imports and configurations
    import autogen
    config_list = autogen.config_list_from_json(
        env_or_file=".config.local",
        file_location=".",
        filter_dict={
            "model": {
                "gpt-4",
                "gpt4",
                "gpt-4-32k",
                "gpt-4-32k-0314",
                "gpt-35-turbo",
                "gpt-3.5-turbo",
            }
        },
    )
    assert len(config_list) > 0
    print("models to use: ", [config_list[i]["model"] for i in range(len(config_list))])
    return config_list


def create_agents(config_list):
    # Create RetrieveAssistantAgent and RetrieveUserProxyAgent instances
    from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
    from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
    import chromadb
    autogen.ChatCompletion.start_logging()

    assistant = RetrieveAssistantAgent(
        name="assistant", 
        system_message="You are a helpful assistant.",
        llm_config={
            "request_timeout": 600,
            "seed": 42,
            "config_list": config_list,
        },
    )
    
    ragproxyagent = RetrieveUserProxyAgent(
        name="ragproxyagent",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        retrieve_config={
            "task": "code",
            "docs_path": "../website/docs/reference",
            "chunk_token_size": 2000,
            "model": config_list[0]["model"],
            "client": chromadb.PersistentClient(path="/tmp/chromadb"),
            "embedding_model": "all-mpnet-base-v2",
        },
    )

    return assistant, ragproxyagent

def create_agents_with_dummy_data(config_list):
    # Create RetrieveAssistantAgent and RetrieveUserProxyAgent instances with dummy data path
    from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
    from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
    import chromadb
    autogen.ChatCompletion.start_logging()

    assistant = RetrieveAssistantAgent(
        name="assistant", 
        system_message="You are a helpful assistant.",
        llm_config={
            "request_timeout": 600,
            "seed": 42,
            "config_list": config_list,
        },
    )
    
    ragproxyagent = RetrieveUserProxyAgent(
        name="ragproxyagent",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        retrieve_config={
            "task": "code",
            "docs_path": "../project_docs/",  # Use the dummy data file
            "chunk_token_size": 2000,
            "model": config_list[0]["model"],
            "client": chromadb.PersistentClient(path="/tmp/chromadb"),
            "embedding_model": "all-mpnet-base-v2",
        },
    )

    return assistant, ragproxyagent

def example_code_problem_with_spark(assistant, ragproxyagent):
    assistant.reset()
    code_problem = "How can I use FLAML to perform a classification task and use spark to do parallel training. Train 30 seconds and force cancel jobs if time limit is reached."
    ragproxyagent.initiate_chat(assistant, problem=code_problem, search_string="spark")


def example_qa_problem_flaml_author(assistant, ragproxyagent):
    assistant.reset()
    qa_problem = "Who is the author of FLAML?"
    ragproxyagent.initiate_chat(assistant, problem=qa_problem)


def example_time_series_forecasting(assistant, ragproxyagent):
    assistant.reset()
    ragproxyagent.human_input_mode = "ALWAYS"
    code_problem = "how to build a time series forecasting model for stock price using FLAML?"
    ragproxyagent.initiate_chat(assistant, problem=code_problem)


def example_function_query_flaml(assistant, ragproxyagent):
    assistant.reset()
    ragproxyagent.human_input_mode = "ALWAYS"
    qa_problem = "Is there a function named `tune_automl` in FLAML?"
    ragproxyagent.initiate_chat(assistant, problem=qa_problem)


# Note: The Natural Questions example requires an external dataset, we will handle it in the next step.
# For now, let's continue with the dummy data creation.


# Note: The Natural Questions example requires an external dataset. 
# This part is excluded from the structured script due to its dependency on the external dataset.

if __name__ == "__main__":
    config_list = initial_setup()
    assistant, ragproxyagent = create_agents_with_dummy_data(config_list)
    example_code_problem_with_spark(assistant, ragproxyagent)
    example_qa_problem_flaml_author(assistant, ragproxyagent)
    example_time_series_forecasting(assistant, ragproxyagent)
    example_function_query_flaml(assistant, ragproxyagent)
