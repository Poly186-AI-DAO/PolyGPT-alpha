
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json, GroupChat, GroupChatManager

config_list_gpt4 = config_list_from_json(
    "../OAI_CONFIG_LIST.json",
    filter_dict={
        "model": ["gpt-4-0613", "gpt-4", "gpt-4-0314"],
    },
)

gpt4_config = {
    "seed": 42,  # change the seed for different trials
    "temperature": 0,
    "config_list": config_list_gpt4,
    "request_timeout": 120,
}
user_proxy = UserProxyAgent(
   name="Admin",
   system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.",
   code_execution_config=False,
)
engineer = AssistantAgent(
    name="Engineer",
    llm_config=gpt4_config,
    system_message='''Engineer. You follow an approved plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
''',
)
scientist = AssistantAgent(
    name="Scientist",
    llm_config=gpt4_config,
    system_message="""Scientist. You follow an approved plan. 
    You are able to read and understand papers. 
    You don't write code. 
    You must suggest the application of the discoveries found in the papers """
)
planner = AssistantAgent(
    name="Planner",
    system_message='''Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
The plan may involve an engineer who can write code and a scientist who doesn't write code.
Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a scientist.
''',
    llm_config=gpt4_config,
)
executor = UserProxyAgent(
    name="Executor",
    system_message="Executor. Execute the code written by the engineer and report the result.",
    human_input_mode="NEVER",
    code_execution_config={"last_n_messages": 3, "work_dir": "paper"},
)
critic = AssistantAgent(
    name="Critic",
    system_message='''Critic. Double check plan, claims, code from other agents and provide feedback. 
    Check whether the plan includes adding verifiable info such as source URL.
    ''',
    llm_config=gpt4_config,
)
groupchat = GroupChat(agents=[user_proxy, engineer, scientist, planner, executor, critic], messages=[], max_round=50)
manager = GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)
user_proxy.initiate_chat(
    manager,
    message="""
find papers AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation Framework and Cognitive Architectures for Language Agents, Large Language Model (LLM) as a System of Multiple Expert Agents: An Approach to solve the Abstraction and Reasoning Corpus (ARC) Challenge, A Language-Agent Approach to Formal Theorem-Proving, and Coding by Design: GPT-4 empowers Agile Model Driven Development from arxiv. 
Use a python script to find all papers then print out their overview and exerp
let's discuss these papers.
""",
)