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


# Product Owner
product_owner = autogen.UserProxyAgent(
    name="Product_Owner",
    system_message="A stakeholder defining the requirements for the Stripe Treasury API. Approves features and oversees the project.",
    code_execution_config=False,
)

# Backend Developer
backend_developer = autogen.AssistantAgent(
    name="Backend_Developer",
    llm_config=gpt4_config,
    system_message="Backend developer responsible for writing the FastAPI code, database setup, and Stripe Treasury integration."
)

# QA Tester
qa_tester = autogen.AssistantAgent(
    name="QA_Tester",
    llm_config=gpt4_config,
    system_message="QA tester ensuring the API endpoints meet the requirements, testing, and reporting bugs."
)

# Architect
architect = autogen.AssistantAgent(
    name="Architect",
    llm_config=gpt4_config,
    system_message="System architect designing the overall architecture and ensuring best practices."
)

# DevOps
devops = autogen.AssistantAgent(
    name="DevOps",
    llm_config=gpt4_config,
    system_message="DevOps specialist setting up the deployment infrastructure, ensuring CI/CD, and managing deployments."
)

# Reviewer
reviewer = autogen.AssistantAgent(
    name="Reviewer",
    llm_config=gpt4_config,
    system_message="Code reviewer suggesting improvements and ensuring code quality."
)

group_chat_dev_team = autogen.GroupChat(
    agents=[product_owner, backend_developer,
            qa_tester, architect, devops, reviewer],
    messages=[],
    max_round=50
)

manager = autogen.GroupChatManager(
    groupchat=group_chat_dev_team, llm_config=gpt4_config)

# Initiating Chat
product_owner.initiate_chat(
    manager,
    message="Let's build a FastAPI backend for Stripe Treasury integrations. I'll define requirements and coordinate work. here is the documentation of the api https://stripe.com/docs/treasury/examples/financial-accounts"
)
