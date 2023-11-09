import os
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
import autogen
import requests
from datetime import datetime
import http.client
import json
import base64
import replicate


load_dotenv("../.env")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
SCENEX_JINA = os.getenv("SCENEX_JINA")

config_list = config_list_from_json(env_or_file="../OAI_CONFIG_LIST.json")
llm_config = {"config_list": config_list, "request_timeout": 120}

# function to use llava model to review image

def img_review(image_url, prompt):
    data = {
        "data": [
            {
                "image": "https://picsum.photos/200",
                "features": [],
            },
        ]}

    headers = {
        "x-api-key": SCENEX_JINA,
        "content-type": "application/json",
    }

    connection = http.client.HTTPSConnection("api.scenex.jina.ai")
    connection.request("POST", "/v1/describe", json.dumps(data), headers)
    response = connection.getresponse()

    print(response.status, response.reason)
    response_data = response.read().decode("utf-8")
    print(response_data)

    connection.close()

    return response_data


result = img_review(
    "https://cdn.discordapp.com/attachments/1083723388712919182/1089909178266558554/HannaD_A_captivating_digital_artwork_features_a_red-haired_girl_664d73dc-b537-490e-b044-4fbf22733559.png", "a llama driving a car")
print(result)

def img_review(image_path, prompt):
    output = replicate.run(
        "yorickvp/llava-13b:6bc1c7bb0d2a34e413301fee8f7cc728d2d4e75bfab186aa995f63292bda92fc",
        input={
            "image": open(image_path, "rb"),
            "prompt": f"What is happening in the image? From scale 1 to 10, decide how similar the image is to the text prompt {prompt}?",
        }
    )

    result = ""
    for item in output:
        result += item

    return result


# function to use stability-ai model to generate image
def text_to_image_generation(prompt):
    output = replicate.run(
        "stability-ai/sdxl:c221b2b8ef527988fb59bf24a8b97c4561f1c671f73bd389f866bfb27c061316",
        input={
            "prompt": prompt
        }
    )

    if output and len(output) > 0:
        # Get the image URL from the output
        image_url = output[0]
        print(f"generated image for {prompt}: {image_url}")

        # Download the image and save it with a filename based on the prompt and current time
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        shortened_prompt = prompt[:50]
        filename = f"imgs/{shortened_prompt}_{current_time}.png"

        response = requests.get(image_url, timeout=300)
        if response.status_code == 200:
            with open(filename, "wb") as file:
                file.write(response.content)
            return f"Image saved as '{filename}'"
        else:
            return "Failed to download and save the image."
    else:
        return "Failed to generate the image."


# Create llm config
llm_config_assistants = {
    "functions": [
        {
            "name": "text_to_image_generation",
            "description": "use latest AI model to generate image based on a prompt, return the file path of image generated",
            "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "a great text to image prompt that describe the image",
                        }
                    },
                "required": ["prompt"],
            },
        },
        {
            "name": "image_review",
            "description": "review & critique the AI generated image based on original prompt, decide how can images & prompt can be improved",
            "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "the original prompt used to generate the image",
                        },
                        "image_path": {
                            "type": "string",
                            "description": "the image file path, make sure including the full file path & file extension",
                        }
                    },
                "required": ["prompt", "image_path"],
            },
        },
    ],
    "config_list": config_list,
    "request_timeout": 120}

# Create assistant agent
img_gen_assistant = AssistantAgent(
    name="text_to_img_prompt_expert",
    system_message="You are a text to image AI model expert, you will use text_to_image_generation function to generate image with prompt provided, and also improve prompt based on feedback provided until it is 10/10.",
    llm_config=llm_config_assistants,
    function_map={
        "image_review": img_review,
        "text_to_image_generation": text_to_image_generation
    }
)

img_critic_assistant = AssistantAgent(
    name="img_critic",
    system_message="You are an AI image critique, you will use img_review function to review the image generated by the text_to_img_prompt_expert against the original prompt, and provide feedback on how to improve the prompt.",
    llm_config=llm_config_assistants,
    function_map={
        "image_review": img_review,
        "text_to_image_generation": text_to_image_generation
    }
)

# Create user proxy agent
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="ALWAYS",
)

# Create groupchat
groupchat = autogen.GroupChat(
    agents=[user_proxy, img_gen_assistant, img_critic_assistant], messages=[], max_round=50)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config)

# Start the conversation
user_proxy.initiate_chat(
    manager, message="Generate a photo realistic image of llama driving a car")