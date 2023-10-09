from autogen import AssistantAgent, UserProxyAgent, config_list_from_json, GroupChat, GroupChatManager
import os
from dotenv import load_dotenv
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

# Load .env file
load_dotenv()

# Configuration for GPT-4
config_list = config_list_from_json(
    "../../OAI_CONFIG_LIST.json",
    filter_dict={
        "model": [
            "gpt-4-0613",
            "gpt-4-0314",
        ],
    },
)

model_config = {
    "seed": 42,
    "temperature": 0,
    "config_list": config_list,
    "request_timeout": 1200,
}

# Initialize API client
api_key = os.getenv('ANTHROPIC_API_KEY')
anthropic = Anthropic(api_key=api_key)

# Define the common working directory for all agents
working_directory = "marketing"

# Create a planner AssistantAgent and UserProxyAgent instances
planner = AssistantAgent(
    name="planner",
    llm_config={"config_list": config_list},
    system_message='''
    Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
The plan may involve an engineer who can write code and a scientist who doesn't write code.
Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a scientist.
'''
)

planner_user = UserProxyAgent(
    name="planner_user",
    max_consecutive_auto_reply=0,
    human_input_mode="NEVER",
)

def ask_planner(message):
    planner_user.initiate_chat(planner, message=message)
    return planner_user.last_message()["content"]

llm_config_functions_caller = {
    "model": "gpt-4-0613",
    "functions": [
        {
            "name": "generate_summary",
            "description": "Generate detailed text or code based on the provided message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to base the generation on. the response will be in a json with a message that you have to extract",
                    },
                },
                "required": ["message"],
            },
        },
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
    "config_list": config_list,
}

def generate_summary(message):
    completion = anthropic.completions.create(
        model="claude-2",
        max_tokens_to_sample=300,
        prompt=f"{HUMAN_PROMPT}{message}{AI_PROMPT}",
    )

    return completion.completion

programmer = AssistantAgent(
    name="Programmer",
    system_message='''Programmer: I'm here to provide detailed explanations and code suggestions. 
If I'm unsure about something, I'll consult the Researcher for online resources. 
Always remember to stay in character and follow the guidelines.''',
    llm_config=config_list,
)

code_executor = UserProxyAgent(
    name="Code_Executor",
    system_message='''Code Executor: My role is to execute the provided code from the Programmer in the designated environment. 
I'll report the outcomes and highlight any potential issues. 
If the code doesn't follow best practices, I'll recommend enhancements to the Programmer.''',
    code_execution_config={
        "work_dir": working_directory,
        "use_docker": False,
        "timeout": 120,
        "last_n_messages": 3,
    },
    human_input_mode="NEVER",
)

user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get(
        "content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "web"},
    llm_config=model_config,
    function_map={
        "ask_planner": ask_planner,
                  "generate_summary": generate_summary
                  },
    system_message='''User: Reply TERMINATE if the task has been solved to your full satisfaction.
Otherwise, reply CONTINUE or specify the reason why the task hasn't been solved yet.''',
)

marking_agent = AssistantAgent(
    name="Marking_Agent",
    llm_config={"config_list": config_list},  # Assuming you have defined 'config_list' earlier in your code
    system_message='''Marking Agent: You are a specialized AI assistant for reviewing and marking content. 
Your primary role is to evaluate answers, essays, code, or any other content provided to you, based on predefined criteria or guidelines. 
Provide constructive feedback and, if possible, suggest improvements. Ensure fairness and consistency in your evaluations.'''
)

marketing_team = GroupChat(
    agents=[user_proxy, marking_agent],
    messages=[],
    max_round=50
)

manager = GroupChatManager(
    groupchat=marketing_team, llm_config=model_config)

user_proxy.initiate_chat(
    manager,
    message="""
    My project is called Autogen, I need your help to create a marketing plan, if you have any questions let me know

    """
)
