from autogen import AssistantAgent, UserProxyAgent

from modules.core_llm.llms_config import LlmConfiguration

# Instantiate the LlmConfiguration with filtering
llm_filters = [
    "gpt-4-32k",
    "gpt-35-turbo-16k",
    "gpt4",
    "gpt-4-0314",
    "gpt-4-0613",
    "gpt-4-32k-0314",
    "gpt-4-32k-v0314"
]
config_list_instance = LlmConfiguration(filter_llms=llm_filters)

set_llm_config = {
    "request_timeout": 600,
    "seed": 42,
    # Accessing the 'config' attribute of our instance
    "config_list": config_list_instance.config,
    "temperature": 0,
}


# Create a planner AssistantAgent and UserProxyAgent instances
planner = AssistantAgent(
    name="planner",
    llm_config={"config_list": config_list_instance.config},
    system_message="You are a helpful AI assistant. You suggest coding and reasoning steps for another AI assistant to accomplish a task. Do not suggest concrete code. For any action beyond writing code or reasoning, convert it to a step which can be implemented by writing code. For example, the action of browsing the web can be implemented by writing code which reads and prints the content of a web page. Finally, inspect the execution result. If the plan is not good, suggest a better plan. If the execution is wrong, analyze the error and suggest a fix."
)
planner_user = UserProxyAgent(
    name="planner_user",
    max_consecutive_auto_reply=0,
    human_input_mode="NEVER",
)


def task_planner(message):
    planner_user.initiate_chat(planner, message=message)
    return planner_user.last_message()["content"]
