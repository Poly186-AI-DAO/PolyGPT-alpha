# Required Libraries
import os
import autogen
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from typing import Optional, Union, Type
import pi
from langchain.tools.file_management.read import ReadFileTool

# Define the configuration list
config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
    },
)

# Define the CircumferenceToolInput class
class CircumferenceToolInput(BaseModel):
    radius: float = Field()

# Define the CircumferenceTool class
class CircumferenceTool(BaseTool):
    name = "circumference_calculator"
    description = "Use this tool when you need to calculate a circumference using the radius of a circle"
    args_schema: Type[BaseModel] = CircumferenceToolInput

    def _run(self, radius: float):
        return float(radius) * 2.0 * pi

# Define a function to generate llm_config from a LangChain tool
def generate_llm_config(tool):
    function_schema = {
        "name": tool.name.lower().replace(' ', '_'),
        "description": tool.description,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }

    if tool.args_schema is None:
        return function_schema
    elif tool.args_schema.__annotations__ is not None:
        for field_name, field in tool.args_schema.__annotations__.items():
            type_mapping = {
                int: 'integer',
                float: 'float',
                str: 'string',
                bool: 'boolean',
                list: 'list',
                tuple: 'tuple',
                dict: 'dictionary',
                set: 'set',
                complex: 'complex'
            }
            full_name = type_mapping[field]

            function_schema["parameters"]["properties"][field_name] = {
                "type": full_name,
                "description": field.__doc__,
            }
            if field_name in getattr(tool.args_schema, "__required_fields__", []):
                function_schema["parameters"]["required"].append(field_name)

    return function_schema

# Instantiate the ReadFileTool and CircumferenceTool
read_file_tool = ReadFileTool()
custom_tool = CircumferenceTool()

# Construct the llm_config
llm_config = {
    "functions": [
        generate_llm_config(read_file_tool),
    ],
    "config_list": config_list,
    "request_timeout": 120,
}

print(llm_config)

# Instantiate the UserProxyAgent
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "coding"},
)

# Register the tool and start the conversation
user_proxy.register_function(
    function_map={
        read_file_tool.name: read_file_tool._run,
    }
)

# Instantiate the AssistantAgent
chatbot = autogen.AssistantAgent(
    name="chatbot",
    system_message="For coding tasks, only use the functions you have been provided with. Reply TERMINATE when the task is done.",
    llm_config=llm_config,
)

# Initiate the chat
user_proxy.initiate_chat(
    chatbot,
    message="Read the file with the path 'Test.txt'.",
    llm_config=llm_config,
)
