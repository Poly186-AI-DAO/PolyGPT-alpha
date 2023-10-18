from autogen import AssistantAgent, UserProxyAgent, config_list_from_json, config_list_openai_aoai

def planner_agent(message: str):
    # Configuration initialization
    config_list = config_list_from_json(
        env_or_file="OAI_CONFIG_LIST.json",
        file_location="C:\\Users\\Shadow\\Documents\\Repo\PolyGPT\\",
        filter_dict={
            "model": [
                "gpt-4-32k",
                "gpt-35-turbo-16k",
            ]
        },
    )

    llm_config = {
        "request_timeout": 600,
        "seed": 42,
        "config_list": config_list,
        "temperature": 0,
    }

    # Create a planner AssistantAgent and UserProxyAgent instances
    planner_agent_assistant = AssistantAgent(
        name="Planner_Agent_Assistant",
        llm_config=llm_config,
        system_message='''Planner_Agent_Assistant.
        You suggest coding and reasoning steps for the Planner_Agent. 
        Do not suggest concrete code. 
        For any action beyond writing code or reasoning, convert it to a step which can be implemented by writing code. 
        For example, the action of browsing the web can be implemented by writing code which reads and prints the content of a web page. 
        Inspect the execution result. If the plan is not good, suggest a better plan. 
        If the execution is wrong, analyze the error and suggest a fix.
        Do not terminate a task on your own. 
        Wait for instructions from Planner_Agent.
        '''
    )

    planner_agent = UserProxyAgent(
        name="Planner_Agent",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get(
            "content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={"work_dir": "../../tools"},
        llm_config=llm_config,
        system_message='''
        Planner_Agent.
        You are the primary interface between the user and the assistant. 
        Direct the Planner_Agent_Assistant to accomplish tasks.
        Only terminate the task when you're fully satisfied or if the user indicates so. 
        If not satisfied, provide a clear reason for the dissatisfaction or reply CONTINUE to keep the task ongoing. 
        Ensure the user is aware they can reply TERMINATE if the task has been solved to full satisfaction.
        '''
    )


    # Initiate a chat with the assistant using the provided message
    planner_agent.initiate_chat(
        planner_agent_assistant,
        message=message,
    )
