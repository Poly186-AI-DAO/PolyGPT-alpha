import json
from flaml import autogen

# # create a text completion request
# response = autogen.oai.Completion.create(
#     config_list=[
#         {
#             "model": "chatglm",
#             "api_base": "http://localhost:8080/v1",
#             "api_type": "open_ai",
#             "api_key": "NULL", # just a placeholder
#         }
#     ],
#     prompt="Once a upon a time, if a land ....",
# )
# print(response)

# create a chat completion request
response = autogen.oai.ChatCompletion.create(
    config_list=[
        {
            "model": "chatglm",
            "api_base": "http://localhost:8080/v1",
            "api_type": "open_ai",
            "api_key": "NULL",
        }
    ],
    messages=[{"role": "user", "content": "what are you capable of ?"}]
)
print(response)