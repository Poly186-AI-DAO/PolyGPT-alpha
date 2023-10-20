from autogen import AssistantAgent, UserProxyAgent, config_list_from_json, GroupChat, GroupChatManager


def research_team(message: str):
    """
    Initiate a multi-agent chat to research and discuss the given message or task.
    :param message: The task or question for the research team.
    :return: None
    """
    # Configuration setup
    config_list = config_list_from_json(
        env_or_file="OAI_CONFIG_LIST.json",
        file_location="C:\\Users\\Shadow\\Documents\\Repo\PolyGPT\\",
        filter_dict={
            "model": [
                "gpt-4-32k",
                "gpt-35-turbo-16k",
                "gpt4",
                "gpt-4-0314",
                "gpt-4-0613",
                "gpt-4-32k-0314",
                "gpt-4-32k-v0314"
            ]
        },
    )

    gpt4_config = {
        "seed": 42,  # Change the seed for different trials
        "temperature": 0,
        "config_list": config_list,
        "request_timeout": 120,
    }

    # Agent setup
    user_proxy = UserProxyAgent(
        name="Admin",
        system_message=''' 
        Admin. 
        The central authority in the research group. 
        Your role is to interact with the planner, scrutinizing and endorsing plans. 
        You hold the power to greenlight the implementation of the strategy. 
        Your approval is vital before any plan execution.
        ''',
        code_execution_config=False,
    )

    engineer = AssistantAgent(
        name="Engineer",
        llm_config=gpt4_config,
        system_message='''Engineer. 
        You are the coding specialist in this research team. 
        Always operate within the boundaries of an approved plan. 
        Your primary task is to develop python/shell scripts that fulfill the objectives of the given task. 
        Adherence to coding standards is imperative. 
        Do not create incomplete codes or those that need external amendments.
        ''',
    )

    scientist = AssistantAgent(
        name="Scientist",
        llm_config=gpt4_config,
        system_message='''
        Scientist. 
        Your expertise lies in deciphering and leveraging the knowledge from academic papers. 
        While you strictly adhere to the approved plan, you do not indulge in coding. 
        Your primary contribution is recommending how the revelations in papers can be practically implemented or beneficial to the task at hand.
        ''',
    )

    planner = AssistantAgent(
        name="Planner",
        system_message='''
        Planner. 
        You are the strategist of the team, formulating plans that leverage the skills of both the engineer and scientist. 
        Your plans should be precise, segregating tasks based on roles. 
        It's vital to adapt, refining your strategies based on feedback, until the admin provides a stamp of approval.
        ''',
        llm_config=gpt4_config,
    )

    executor = UserProxyAgent(
        name="Executor",
        system_message='''
        Executor.
        As the name suggests, you bring plans to life by running the code crafted by the engineer. 
        It's crucial that you promptly report back with the outcomes, ensuring the engineer is abreast of the results to make any necessary adjustments.
        ''',
        human_input_mode="NEVER",
        code_execution_config={"last_n_messages": 3, "work_dir": "research"},
    )

    critic = AssistantAgent(
        name="Critic",
        system_message='''
        Critic. 
        Your sharp analytical skills are crucial for the team. 
        Your duty is to meticulously review plans, verify claims, and scrutinize codes. 
        Always provide constructive feedback and ensure that every strategy has valid, traceable references such as URLs to ensure the team is grounded in verifiable information.
        ''',
        llm_config=gpt4_config,
    )

    # Create a group chat with all agents
    groupchat = GroupChat(agents=[user_proxy, engineer, scientist,
                          planner, executor, critic], messages=[], max_round=50)
    manager = GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)

    # Initiate a chat with the manager (which controls all agents)
    user_proxy.initiate_chat(manager, message=message)
