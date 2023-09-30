
'''
The AutoGen library provides a multi-agent conversation framework for integrating 
LLMs, tools, and humans via agent-based conversations.

Key components:

UserProxyAgent - Acts as a human user proxy in the conversation. 
AssistantAgent - Powered by an LLM like GPT-3.5 or GPT-4.
GroupChat - Manages a conversation between multiple agents.
GroupChatManager - Orchestrates the group chat workflow.

To initialize a conversation:

1. Create agents and configure their capabilities
2. Initialize a GroupChat with the agents 
3. Create a GroupChatManager
4. Call `initiate_chat()` on a UserProxyAgent or AssistantAgent

The `initiate_chat()` method starts a conversation by sending the message to the 
GroupChatManager. The manager facilitates the exchange of messages between agents. 

Additional capabilities like code execution can be configured on the agents and 
orchestrated through the chat.

This provides a flexible framework for automating conversations and workflows between
humans, LLMs, APIs, and other tools.
'''

# Import AutoGen library
from flaml import autogen

# Create GPT-4 configuration
# This provides access credentials for GPT-4 models
config_list = autogen.config_list_from_json(
    "../OAI_CONFIG_LIST.json",
    filter_dict={
        "model": ["gpt-4-0613", "gpt-4-32k", "gpt-4", "gpt-4-0314", "gpt-3.5-turbo", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613", "gpt-35-turbo-16k"],
    }
)

model_config = {
    "seed": 42,
    "temperature": 0,
    "config_list": config_list,
    "request_timeout": 1200
}

working_directory = "project_files"

# the purpose of the following line is to log the conversation history
autogen.ChatCompletion.start_logging()

# Create user agent
# Acts as human user in the conversation
user = autogen.UserProxyAgent(
    name="User",
    system_message="End user of the product. Validates features meet requirements."

)

# Product Manager - UserProxyAgent
product_manager = autogen.UserProxyAgent(
    name="Product_Manager",
    system_message='''Product Manager: Defines product requirements, prioritizes features, and coordinates work across the team.  Verify that all project files are available
    Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
The plan may involve an engineer who can write code and a scientist who doesn't write code.
Explain the plan first. Be clear which step is performed by an developer/engineer, and which step is performed by the web_surfer, developer, code_executor, code_reviewer.
''',
    code_execution_config={
        "work_dir": working_directory,
        "use_docker": False,
        "timeout": 120,
        "last_n_messages": 6,
    }
)

# Web Surfer
web_surfer = autogen.UserProxyAgent(
    name="Web_Surfer",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get(
        "content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "web"},
    llm_config=model_config,
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
Otherwise, reply CONTINUE, or the reason why the task is not solved yet."""
)

#  Developer
developer = autogen.AssistantAgent(
    name="Developer",
    llm_config=model_config,
    system_message='''Engineer. You follow an approved plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
'''
)

# Code Executor - UserProxyAgent
code_executor = autogen.UserProxyAgent(
    name="Code_Executor",
    system_message="Runs code snippets. Validates behavior and results. Provides outputs. Verify that all project files are available",
    code_execution_config={
        "work_dir": working_directory,
        "use_docker": False,
        "timeout": 120,
        "last_n_messages": 3,
    },
    human_input_mode="NEVER",
)

# Code Reviewer - AssistantAgent
code_reviewer = autogen.AssistantAgent(
    name="Code_Reviewer",
    llm_config=model_config,
    system_message="Reviews code quality, security, efficiency, and style. Provides feedback. Develops test cases. Tests code thoroughly. Reports bugs and issues."
)

# Create group chat
# Manages conversation between agents
chat = autogen.GroupChat(
    agents=[user, product_manager, web_surfer,
            developer, code_executor, code_reviewer],
    messages=[]
)

# Create chat manager
# Orchestrates messaging between agents
manager = autogen.GroupChatManager(
    groupchat=chat,
    llm_config=model_config
)

# Initialize conversation
# Send initial message to manager
user.initiate_chat(manager, message="Let's build a Stripe Backend using Fast API, here is a github sample project that you can clone locally then copy the backend code from the next.js api folder and convert the code into python https://github.com/stripe-samples/issuing-treasury")
