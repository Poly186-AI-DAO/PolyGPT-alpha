from flaml import autogen

# Configuration for GPT-4
config_list_gpt4 = autogen.config_list_from_json(
    "../OAI_CONFIG_LIST.json",
    filter_dict={
        "model": ["gpt-4-0613, gpt-4-32k, gpt-4, gpt-4-0314"],
    },
)

gpt4_config = {
    "seed": 42,
    "temperature": 0,
    "config_list": config_list_gpt4,
    "request_timeout": 1200,
}

working_directory = "game_files"  # Common working directory for relevant agents

# Player - UserProxyAgent
player = autogen.UserProxyAgent(
    name="Player",
    system_message="Player: Provide feedback on gameplay. Collaborate with the Game Designer for enhancing the game.",
    code_execution_config={
        "work_dir": working_directory,
        "use_docker": False,
        "timeout": 120,
        "last_n_messages": 1,
    },
)

# Game Designer - AssistantAgent
game_designer = autogen.AssistantAgent(
    name="Game_Designer",
    llm_config=gpt4_config,
    system_message="Game Designer: Craft the design for the snake game. Document details in 'game_design.txt'. Collaborate for a comprehensive design."
)

# Programmer - AssistantAgent
programmer = autogen.AssistantAgent(
    name="Programmer",
    llm_config=gpt4_config,
    system_message="Programmer: Develop the snake game. Save code in the working directory. Use a venv for dependency management and create/maintain 'requirements.txt'."
)

# Game Tester - UserProxyAgent
game_tester = autogen.UserProxyAgent(
    name="Game_Tester",
    system_message="Game Tester: Playtest the game. Share feedback on gameplay, mechanics, and possible bugs.",
    code_execution_config={
        "work_dir": working_directory,
        "use_docker": False,
        "timeout": 120,
        "last_n_messages": 3,
    },
    human_input_mode="ALWAYS",
)

# Code Executor - UserProxyAgent
code_executor = autogen.UserProxyAgent(
    name="Code_Executor",
    system_message="Code Executor: Run the given code in the specified environment. Report outcomes and potential problems.",
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
    llm_config=gpt4_config,
    system_message="Code Reviewer: Inspect the given code. Ensure its quality, efficiency, and adherence to best practices. Recommend enhancements."
)

# Internet Researcher - AssistantAgent
internet_researcher = autogen.AssistantAgent(
    name="Internet_Researcher",
    llm_config=gpt4_config,
    system_message="Internet Researcher: Explore relevant game development trends. Offer insights and references."
)

# File Management Agent - AssistantAgent
file_manager = autogen.AssistantAgent(
    name="File_Manager",
    llm_config=gpt4_config,
    system_message="File Manager: Create, read, and write local files as needed. Save work and progress of the team."
)

# Group Chat Setup
groupchat = autogen.GroupChat(
    agents=[player, game_tester, game_designer, programmer,
            code_executor, code_reviewer, internet_researcher, file_manager],
    messages=[],
    max_round=150  # Increased max_round for extended interaction
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)

# Initiating Chat
player.initiate_chat(
    manager,
    message="Let's design and implement a snake game. I aim for it to be entertaining and challenging."
)
