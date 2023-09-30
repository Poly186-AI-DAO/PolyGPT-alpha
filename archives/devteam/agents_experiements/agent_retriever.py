# Imports
import autogen
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import chromadb
import json
import os

# Configurations


def setup_config():
    config_list = autogen.config_list_from_json(
        "../../OAI_CONFIG_LIST.json",
        filter_dict={
            "model": [
                "gpt-4-0613",
                "gpt-4-32k",
                "gpt-4",
                "gpt-4-0314",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-0613",
                "gpt-3.5-turbo-0301",
                "gpt-3.5-turbo-16k",
                "gpt-3.5-turbo-16k-0613",
                "gpt-35-turbo-16k"
            ],
        },
    )

    assert len(config_list) > 0

    print("Models to use: ", [config_list[i]["model"]
          for i in range(len(config_list))])

    return config_list

# Agent creation


def create_agents(config_list):
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
            "docs_path": "../../project_docs/",
            "chunk_token_size": 2000,
            "model": config_list[0]["model"],
            "client": chromadb.PersistentClient(path="/tmp/chromadb"),
            "embedding_model": "all-mpnet-base-v2",
        },
    )
    return assistant, ragproxyagent

# Example conversations


def example_code_problem(assistant, ragproxyagent):
    assistant.reset()
    code_problem = "How can I use FLAML to perform a classification task and use spark to do parallel training. Train 30 seconds and force cancel jobs if time limit is reached."
    ragproxyagent.initiate_chat(
        assistant, problem=code_problem, search_string="spark")


def example_qa_problem(assistant, ragproxyagent):
    assistant.reset()
    qa_problem = "What is the Poly Bank"
    ragproxyagent.initiate_chat(assistant, problem=qa_problem)


def example_time_series_forecasting(assistant, ragproxyagent):
    assistant.reset()
    ragproxyagent.human_input_mode = "ALWAYS"
    code_problem = "how to build using AutoGen ?"
    ragproxyagent.initiate_chat(assistant, problem=code_problem)


def example_function_query(assistant, ragproxyagent):
    assistant.reset()
    ragproxyagent.human_input_mode = "ALWAYS"
    qa_problem = "Is there a document about SESAP ?"
    ragproxyagent.initiate_chat(assistant, problem=qa_problem)


def example_natural_questions(assistant, config_list):
    print("Setting model in config_list to gpt-35-turbo...")
    config_list[0]["model"] = "gpt-35-turbo"

    print("Setting corpus_file path...")
    corpus_file = "https://huggingface.co/datasets/thinkall/NaturalQuestionsQA/resolve/main/corpus.txt"

    print("Initializing RetrieveUserProxyAgent...")
    ragproxyagent = RetrieveUserProxyAgent(
        name="ragproxyagent",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        retrieve_config={
            "task": "qa",
            "docs_path": corpus_file,
            "chunk_token_size": 2000,
            "model": config_list[0]["model"],
            "client": chromadb.PersistentClient(path="/tmp/chromadb"),
            "collection_name": "natural-questions",
            "chunk_mode": "one_line",
            "embedding_model": "all-MiniLM-L6-v2",
        },
    )

    print("Defining provided queries...")

    queries = """{"_id": "ce2342e1feb4e119cb273c05356b33309d38fa132a1cbeac2368a337e38419b8", "text": "what is non controlling interest on balance sheet", "metadata": {"answer": ["the portion of a subsidiary corporation 's stock that is not owned by the parent corporation"]}}
{"_id": "3a10ff0e520530c0aa33b2c7e8d989d78a8cd5d699201fc4b13d3845010994ee", "text": "how many episodes are in chicago fire season 4", "metadata": {"answer": ["23"]}}
{"_id": "fcdb6b11969d5d3b900806f52e3d435e615c333405a1ff8247183e8db6246040", "text": "what are bulls used for on a farm", "metadata": {"answer": ["breeding", "as work oxen", "slaughtered for meat"]}}
{"_id": "26c3b53ec44533bbdeeccffa32e094cfea0cc2a78c9f6a6c7a008ada1ad0792e", "text": "has been honoured with the wisden leading cricketer in the world award for 2016", "metadata": {"answer": ["Virat Kohli"]}}
{"_id": "0868d0964c719a52cbcfb116971b0152123dad908ac4e0a01bc138f16a907ab3", "text": "who carried the usa flag in opening ceremony", "metadata": {"answer": ["Erin Hamlin"]}}
"""
    print("Parsing provided queries...")

    queries = [json.loads(line) for line in queries.split("\n") if line]
    questions = [q["text"] for q in queries]

    print("Initiating chat for each question...")
    for i in range(len(questions)):
        print(
            f"\n\n>>>>>>>>>>>>  Below are outputs of Case {i+1}  <<<<<<<<<<<<\n\n")

        assistant.reset()
        qa_problem = questions[i]
        ragproxyagent.initiate_chat(
            assistant, problem=qa_problem, n_results=30)


def main():
    config_list = setup_config()
    assistant, ragproxyagent = create_agents(config_list)

    # Present a menu to the user to choose which example to run
    print("\nChoose an example to run:")
    print("1: Code Problem")
    print("2: QA Problem")
    print("3: Time Series Forecasting")
    print("4: Function Query")
    print("5: Natural Questions")
    choice = int(input("Enter your choice (1-5): "))

    if choice == 1:
        example_code_problem(assistant, ragproxyagent)
    elif choice == 2:
        example_qa_problem(assistant, ragproxyagent)
    elif choice == 3:
        example_time_series_forecasting(assistant, ragproxyagent)
    elif choice == 4:
        example_function_query(assistant, ragproxyagent)
    elif choice == 5:
        example_natural_questions(assistant, config_list)
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
