
# Required imports
from flaml import autogen
import json

# Configuration initialization
config_list = autogen.config_list_from_json(
    "../OAI_CONFIG_LIST.json",
    filter_dict={
        "model": ["gpt-4", "gpt-4-0314", "gpt4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
    },
)

# Create a planner AssistantAgent and UserProxyAgent instances
planner = autogen.AssistantAgent(
    name="planner",
    llm_config={"config_list": config_list},
    system_message="You are a helpful AI assistant. You suggest coding and reasoning steps for another AI assistant to accomplish a task. Do not suggest concrete code. For any action beyond writing code or reasoning, convert it to a step which can be implemented by writing code. For example, the action of browsing the web can be implemented by writing code which reads and prints the content of a web page. Finally, inspect the execution result. If the plan is not good, suggest a better plan. If the execution is wrong, analyze the error and suggest a fix."
)
planner_user = autogen.UserProxyAgent(
    name="planner_user",
    max_consecutive_auto_reply=0,
    human_input_mode="NEVER",
)

def ask_planner(message):
    planner_user.initiate_chat(planner, message=message)
    return planner_user.last_message()["content"]

# Create an AssistantAgent and UserProxyAgent instances for the main assistant
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={
        "temperature": 0,
        "request_timeout": 600,
        "seed": 42,
        "model": "gpt-4-0613",
        "config_list": autogen.config_list_openai_aoai(exclude="aoai"),
        "functions": [
            {
                "name": "ask_planner",
                "description": "ask planner to: 1. get a plan for finishing a task, 2. verify the execution result of the plan and potentially suggest new plan.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "question to ask planner. Make sure the question include enough context, such as the code and the execution result. The planner does not know the conversation between you and the user, unless you share the conversation with the planner.",
                        },
                    },
                    "required": ["message"],
                },
            },
        ],
    }
)
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "planning"},
    function_map={"ask_planner": ask_planner},
)

# Define a task and initiate a chat with the assistant
user_proxy.initiate_chat(
    assistant,
    message="Suggest a fix to an open good first issue of flaml",
)

print("Script execution completed!")
