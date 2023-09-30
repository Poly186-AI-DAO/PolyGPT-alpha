from flaml import autogen
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

# Configuration for GPT-4
config_list_gpt4 = autogen.config_list_from_json("../OAI_CONFIG_LIST.json", filter_dict={
    "model": ["gpt-4-0613", "gpt-4-32k", "gpt-4", "gpt-4-0314"],
})
gpt4_config = {
    "seed": 42,
    "temperature": 0, 
    "config_list": config_list_gpt4,
    "request_timeout": 1200,
}

working_directory = "project_files"

# Product Manager - UserProxyAgent
product_manager = autogen.UserProxyAgent(
    name="Product_Manager",
    system_message="Product Manager: Define product requirements and priorities. Coordinate work across the team.",
    code_execution_config={
        "work_dir": working_directory,
        "use_docker": False,
        "timeout": 120,
        "last_n_messages": 1,
    }
)

# create a UserProxyAgent instance named "user_proxy"
web_surfer = autogen.UserProxyAgent(
    name="Web_Surfer",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "web"},
    llm_config=gpt4_config,
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
Otherwise, reply CONTINUE, or the reason why the task is not solved yet."""
)

# # Lead Engineer - AssistantAgent 
# lead_engineer = RetrieveAssistantAgent(
#     name="Lead_Engineer",
#     llm_config=gpt4_config,
#     system_message="Lead Engineer: Architect and lead the technical design. Ensure best practices are followed."
# )

# # Backend Engineer Agent 
# backend_engineer = RetrieveUserProxyAgent(
#    name="Backend_Engineer",  
#    retrieve_config={
#       "task": "code",
#       "docs_path": "project_docs", 
#       "chunk_token_size": 2000,
#    }
# )

# DevOps Engineer - AssistantAgent
devops_engineer = autogen.AssistantAgent(
    name="DevOps_Engineer",
    llm_config=gpt4_config, 
    system_message="DevOps Engineer: Set up and manage the development and production environments. Enable continuous integration and deployment." 
)

# QA Engineer - UserProxyAgent 
qa_engineer = autogen.UserProxyAgent(
    name="QA_Engineer", 
    system_message="QA Engineer: Develop and execute test cases. Identify defects and quality issues.",
    code_execution_config={
        "work_dir": working_directory,
        "use_docker": False,
        "timeout": 120, 
        "last_n_messages": 1,
    }
)

# Security Engineer - AssistantAgent
security_engineer = autogen.AssistantAgent(
    name="Security_Engineer",
    llm_config=gpt4_config,
    system_message="Security Engineer: Conduct security reviews. Recommend improvements to address vulnerabilities."
)

# File Manager - UserProxyAgent
file_manager = autogen.UserProxyAgent(
    name="File_Manager", 
    system_message="File Manager: Manage files and artifacts generated during development. Ensure proper versioning.",
    code_execution_config={
        "work_dir": working_directory,
        "use_docker": False,
        "timeout": 120,
        "last_n_messages": 1,
    }
)

# Group Chat Setup
groupchat = autogen.GroupChat(
    agents=[
        web_surfer,
        product_manager,
        devops_engineer,
        qa_engineer,
        security_engineer,
        file_manager
    ],
    messages=[],
    max_round=150
)

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)

# Initiating Chat
product_manager.initiate_chat(manager, message="Let's build a FastAPI backend for Stripe Treasury integrations. I'll define requirements and coordinate work. here is the documentation of the api https://stripe.com/docs/treasury/examples/financial-accounts")