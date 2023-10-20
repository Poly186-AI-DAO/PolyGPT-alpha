from autogen import AssistantAgent, UserProxyAgent

from llms_config import LlmConfiguration

def internet_agent(message: str):
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
    
    llm_config = {
        "request_timeout": 600,
        "seed": 42,
        "config_list": config_list_instance.config, # Accessing the 'config' attribute of our instance
        "temperature": 0,
    }

    # Construct agents
    internet_agent_assistant = AssistantAgent(
        name="Internet_Agent_Assistant ",
        llm_config=llm_config,
        system_message='''
        Internet_Agent_Assistant. 
        You are here to support the Internet_Agent. 
        Respond to queries and provide relevant information as per the task. 
        Follow the directives set by Internet_Agent. 
        Do not terminate a task on your own. 
        Wait for instructions from Internet_Agent.
        '''
    )

    internet_agent = UserProxyAgent(
        name="Internet_Agent",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get(
            "content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={"work_dir": "../../tools"},
        llm_config=llm_config,
        system_message='''Internet_Agent.
        You must use a function to search the internet, if the function doesn't exist in the tools dir then create one, otherwise use the available tools
        You are the primary interface between the user and the assistant. 
        Direct the Internet_Agent_Assistant to accomplish tasks.
        Only terminate the task when you're fully satisfied or if the user indicates so. 
        If not satisfied, provide a clear reason for the dissatisfaction or reply CONTINUE to keep the task ongoing. 
        Ensure the user is aware they can reply TERMINATE if the task has been solved to full satisfaction.
        '''
    )

    # Start a conversation
    internet_agent.initiate_chat(
        internet_agent_assistant,
        message=message
    )
