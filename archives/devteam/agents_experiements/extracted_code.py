# %pip install "pyautogen[retrievechat]~=0.1.0" flaml

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

from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import chromadb

autogen.ChatCompletion.start_logging()

# 1. create an RetrieveAssistantAgent instance named "assistant"
assistant = RetrieveAssistantAgent(
    name="assistant", 
    system_message="You are a helpful assistant.",
    llm_config={
        "request_timeout": 600,
        "seed": 42,
        "config_list": config_list,
    },
)

# 2. create the RetrieveUserProxyAgent instance named "ragproxyagent"
# By default, the human_input_mode is "ALWAYS", which means the agent will ask for human input at every step. We set it to "NEVER" here.
# `docs_path` is the path to the docs directory. By default, it is set to "./docs". Here we generated the documentations from FLAML's docstrings.
# Navigate to the website folder and run `pydoc-markdown` and it will generate folder `reference` under `website/docs`.
# `task` indicates the kind of task we're working on. In this example, it's a `code` task.
# `chunk_token_size` is the chunk token size for the retrieve chat. By default, it is set to `max_tokens * 0.6`, here we set it to 2000.
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

# reset the assistant. Always reset the assistant before starting a new conversation.
assistant.reset()

# given a problem, we use the ragproxyagent to generate a prompt to be sent to the assistant as the initial message.
# the assistant receives the message and generates a response. The response will be sent back to the ragproxyagent for processing.
# The conversation continues until the termination condition is met, in RetrieveChat, the termination condition when no human-in-loop is no code block detected.
# With human-in-loop, the conversation will continue until the user says "exit".
code_problem = "How can I use FLAML to perform a classification task and use spark to do parallel training. Train 30 seconds and force cancel jobs if time limit is reached."
ragproxyagent.initiate_chat(assistant, problem=code_problem, search_string="spark")  # search_string is used as an extra filter for the embeddings search, in this case, we only want to search documents that contain "spark".

# reset the assistant. Always reset the assistant before starting a new conversation.
assistant.reset()

qa_problem = "Who is the author of FLAML?"
ragproxyagent.initiate_chat(assistant, problem=qa_problem)

# reset the assistant. Always reset the assistant before starting a new conversation.
assistant.reset()

# set `human_input_mode` to be `ALWAYS`, so the agent will ask for human input at every step.
ragproxyagent.human_input_mode = "ALWAYS"
code_problem = "how to build a time series forecasting model for stock price using FLAML?"
ragproxyagent.initiate_chat(assistant, problem=code_problem)

# reset the assistant. Always reset the assistant before starting a new conversation.
assistant.reset()

# set `human_input_mode` to be `ALWAYS`, so the agent will ask for human input at every step.
ragproxyagent.human_input_mode = "ALWAYS"
qa_problem = "Is there a function named `tune_automl` in FLAML?"
ragproxyagent.initiate_chat(assistant, problem=qa_problem)

config_list[0]["model"] = "gpt-35-turbo"  # change model to gpt-35-turbo

corpus_file = "https://huggingface.co/datasets/thinkall/NaturalQuestionsQA/resolve/main/corpus.txt"

# Create a new collection for NaturalQuestions dataset
# `task` indicates the kind of task we're working on. In this example, it's a `qa` task.
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

import json

# queries_file = "https://huggingface.co/datasets/thinkall/NaturalQuestionsQA/resolve/main/queries.jsonl"
queries = """{"_id": "ce2342e1feb4e119cb273c05356b33309d38fa132a1cbeac2368a337e38419b8", "text": "what is non controlling interest on balance sheet", "metadata": {"answer": ["the portion of a subsidiary corporation 's stock that is not owned by the parent corporation"]}}
{"_id": "3a10ff0e520530c0aa33b2c7e8d989d78a8cd5d699201fc4b13d3845010994ee", "text": "how many episodes are in chicago fire season 4", "metadata": {"answer": ["23"]}}
{"_id": "fcdb6b11969d5d3b900806f52e3d435e615c333405a1ff8247183e8db6246040", "text": "what are bulls used for on a farm", "metadata": {"answer": ["breeding", "as work oxen", "slaughtered for meat"]}}
{"_id": "26c3b53ec44533bbdeeccffa32e094cfea0cc2a78c9f6a6c7a008ada1ad0792e", "text": "has been honoured with the wisden leading cricketer in the world award for 2016", "metadata": {"answer": ["Virat Kohli"]}}
{"_id": "0868d0964c719a52cbcfb116971b0152123dad908ac4e0a01bc138f16a907ab3", "text": "who carried the usa flag in opening ceremony", "metadata": {"answer": ["Erin Hamlin"]}}
"""
queries = [json.loads(line) for line in queries.split("\n") if line]
questions = [q["text"] for q in queries]
answers = [q["metadata"]["answer"] for q in queries]
print(questions)
print(answers)

for i in range(len(questions)):
    print(f"\n\n>>>>>>>>>>>>  Below are outputs of Case {i+1}  <<<<<<<<<<<<\n\n")

    # reset the assistant. Always reset the assistant before starting a new conversation.
    assistant.reset()
    
    qa_problem = questions[i]
    ragproxyagent.initiate_chat(assistant, problem=qa_problem, n_results=30)