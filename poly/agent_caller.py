from flaml import autogen
from internet_agent import use_internet_agent
from planner_agent import initiate_planner_chat

# Define the agent_caller's functions
def call_agent(agent_function, message):
    """General function to call a specific agent with a message."""
    return agent_function(message)

# Create the agent_caller
agent_caller = autogen.UserProxyAgent(
    name="agent_caller",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "interactions"},
    function_map={
        "initiate_planner_chat": initiate_planner_chat,
        "use_internet_agent": use_internet_agent,
    }
)

# Create an AssistantAgent for the main assistant
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
                "name": "initiate_planner_chat",
                "description": "Ask the planner to provide a plan for a given task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Question or task for the planner.",
                        },
                    },
                    "required": ["message"],
                },
            },
            {
                "name": "use_internet_agent",
                "description": "Use the internet agent to browse the web and fetch information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Instructions or queries for the internet agent.",
                        },
                    },
                    "required": ["message"],
                },
            },
        ],
    }
)

# Initiate a chat with the assistant using the agent_caller
agent_caller.initiate_chat(
    assistant, 
    message=(
        "I have a two-step task for you:\n"
        "1. First, use the planner tool to provide a plan on how to find information about Poly186.\n"
        "2. Once you have a plan, use the internet agent to execute the plan and fetch the information about Poly186.\n"
        "Please proceed in the order mentioned."
    )
)
