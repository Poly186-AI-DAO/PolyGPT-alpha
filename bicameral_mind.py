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

# Define sub-agents
left_agent = autogen.AssistantAgent(
   name="LeftBrain",
   system_message="Focused on logic, language, reasoning"
)

right_agent = autogen.AssistantAgent(
   name="RightBrain",
   system_message="Focused on creativity, emotion, intuition"
) 

# Manager agent 
manager_agent = autogen.AssistantAgent(
   name="Manager",
   llm_config=gpt4_config,
   system_message="Coordinates synthesis and issues final plan to other assistant agents"
)

# Set up group chat
brain_chat = autogen.GroupChat(
    agents=[left_agent, right_agent, manager_agent],
    messages=[],
    max_round=50
)

manager = autogen.GroupChatManager(
    groupchat=brain_chat, llm_config=gpt4_config)

# Initiating Chat
manager_agent.initiate_chat(
    manager,
    message="Engage in a socratic conversation about the nature of life"
)