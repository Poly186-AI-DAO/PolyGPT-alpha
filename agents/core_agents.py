import logging
from autogen import AssistantAgent, UserProxyAgent, config_list_openai_aoai

import os
import json
from agents.internet_agent import internet_agent

from agents.planner_agent import planner_agent
from agents.research_team import research_team
from llms_config import LlmConfiguration
from utils.chat_type import ChatType
from utils.chat_manager import ChatManager


class CoreAgent:
    def __init__(self, message: str):
            self.message = message
            self.setup_agents()
            self.setup_group_chat()  # Calling the renamed method

    def setup_agents(self):
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
            "config_list": config_list_instance.config,
            "temperature": 0,
        }

        self.user_proxy = UserProxyAgent(
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

        self.engineer = AssistantAgent(
            name="Engineer",
            llm_config=llm_config,
            system_message='''Engineer. 
            You are the coding specialist in this research team. 
            Always operate within the boundaries of an approved plan. 
            Your primary task is to develop python/shell scripts that fulfill the objectives of the given task. 
            Adherence to coding standards is imperative. 
            Do not create incomplete codes or those that need external amendments.
            ''',
        )

        self.scientist = AssistantAgent(
            name="Scientist",
            llm_config=llm_config,
            system_message='''
            Scientist. 
            Your expertise lies in deciphering and leveraging the knowledge from academic papers. 
            While you strictly adhere to the approved plan, you do not indulge in coding. 
            Your primary contribution is recommending how the revelations in papers can be practically implemented or beneficial to the task at hand.
            ''',
        )

        self.planner = AssistantAgent(
            name="Planner",
            system_message='''
            Planner. 
            You are the strategist of the team, formulating plans that leverage the skills of both the engineer and scientist. 
            Your plans should be precise, segregating tasks based on roles. 
            It's vital to adapt, refining your strategies based on feedback, until the admin provides a stamp of approval.
            ''',
            llm_config=llm_config,
        )

        self.executor = UserProxyAgent(
            name="Executor",
            system_message='''
            Executor.
            As the name suggests, you bring plans to life by running the code crafted by the engineer. 
            It's crucial that you promptly report back with the outcomes, ensuring the engineer is abreast of the results to make any necessary adjustments.
            ''',
            human_input_mode="NEVER",
            code_execution_config={
                "last_n_messages": 3, "work_dir": "research"},
        )

        self.critic = AssistantAgent(
            name="Critic",
            system_message='''
            Critic. 
            Your sharp analytical skills are crucial for the team. 
            Your duty is to meticulously review plans, verify claims, and scrutinize codes. 
            Always provide constructive feedback and ensure that every strategy has valid, traceable references such as URLs to ensure the team is grounded in verifiable information.
            ''',
            llm_config=llm_config,
        )

    def setup_group_chat(self):
        """Initialize a group chat among the research team agents."""
        logging.info("Initializing group chat...")

        # Define the order of agents in the conversation
        agents_in_order = [
            self.planner,
            self.scientist,
            self.engineer,
            self.critic,
            self.executor,
            self.user_proxy
        ]

        # Initialize the ChatManager with the agents
        chat_manager = ChatManager(
            name="ResearchTeam",  # Updated name for clarity
            agents=agents_in_order
        )

        # Start a group-based conversation
        chat_manager.start_conversation(
            pattern=ChatType.HIERARCHICAL,
            initial_message=self.message,  # Using the class attribute
            starter_name=self.planner.name,
            agent_order_names=[agent.name for agent in agents_in_order]
        )

        logging.info("Group chat initialized.")
