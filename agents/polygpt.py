
from typing import Any
from agents.agents_initializer import AgentInitializer
from utils.autogen_monitor import AutogenMonitor

from utils.observer import Observable
from utils.poly_logger import PolyLogger
from agents.reaction import Reactions

LOG = PolyLogger(__name__)


class PolyGPTAgents(Observable):
    def __init__(self, database, workspace):
        super().__init__()
        self.agent_monitors = []
        self.data_store = {'chat_history': []}
        self.forge_agent = None
        self.database = database
        self.workspace = workspace
        self.reactions = {}

        # Initialize the task_id and step_id as None
        self.current_task_id = None
        self.current_step_id = None

        self._initialize_agents()

    def _initialize_agents(self):
        self.agent_initializer = AgentInitializer(
            self.database, self.workspace)
        self.agents = self.agent_initializer.agents
        self.groupchat = self.agent_initializer.groupchat
        self.manager = self.agent_initializer.manager
        LOG.info(f"Agents initialized in {self.__class__.__name__} %s", list(
            self.agents.keys()))

        for agent_name, agent in self.agents.items():
            # Ensure that reactions are initialized for each agent
            if agent_name not in self.reactions:
                LOG.info(f"Initializing reactions for agent: {agent_name}")
                self.reactions[agent_name] = Reactions(
                    agent, self.database, self.workspace)
                LOG.info(f"Reactions initialized for agent: {agent_name}")
            else:
                LOG.warning(
                    f"Reactions already initialized for agent: {agent_name}")

            LOG.info(f"Initializing AutogenMonitor for agent: {agent_name}")
            agent_monitor = AutogenMonitor(
                agent, self, self.groupchat, self.manager)
            LOG.info(f"AutogenMonitor initialized for agent: {agent_name}")

            # Add observer for specific events using the default_monitored_methods property
            LOG.info(
                f"Adding observers for default monitored methods for agent: {agent_name}")
            for event_name in agent_monitor.default_monitored_methods:
                LOG.info(
                    f"Adding observer for event: {event_name} for agent: {agent_name}")
                agent_monitor.add_observer(
                    self.receive_notification, event=event_name)
                LOG.info(
                    f"Observer added for event: {event_name} for agent: {agent_name}")

            LOG.info(
                f"Appending agent monitor for agent: {agent_name} to agent_monitors list")
            self.agent_monitors.append(agent_monitor)
            LOG.info(
                f"Agent monitor for agent: {agent_name} appended to agent_monitors list")
            LOG.info(f"Initialized PolyGPTAgents for agent: {agent_name}")
        LOG.info("AutoGenAssistant initialized.")

    def set_forge_agent(self, agent):
        LOG.info(f"Setting ForgeAgent for PolyGPTAgents: {agent}")
        self.forge_agent = agent
        LOG.info(f"ForgeAgent set for PolyGPTAgents: {self.forge_agent}")

    def start_chat(self, user_input, task_id=None, step_id=None):
        self.current_task_id = task_id
        self.current_step_id = step_id
        LOG.info(
            f"Starting chat in {self.__class__.__name__} with user input: {user_input}")
        self.agent_initializer.initiate_chat(user_input)

    def retrieve_data(self, data_type: str):
        data = self.data_store.get(data_type)
        if data is None:
            LOG.warning(f"No data found for type: {data_type}")
        else:
            LOG.info(f"Retrieved data for type: {data_type}: {data}")
        return data

    def update_chat_history(self):
        if self.groupchat:
            chat_history = self.groupchat.messages
            self.update_data('chat_history', chat_history)
            LOG.info(f"Updated chat history: {chat_history}")
        if self.manager:
            manager_history = self.manager.chat_messages
            LOG.info(f"Manager chat history: {manager_history}")

    def update_data(self, data_type: str, new_data: Any):
        if data_type in self.data_store:
            self.data_store[data_type] = new_data
            LOG.info(
                f"Updated data for type: {data_type}: {self.data_store[data_type]}")
        else:
            LOG.warning(f"No data store found for type: {data_type}")

    async def receive_notification(self, event: str, data: Any):
        try:
            LOG.info(
                f"Received notification for event: {event} with data: {data}")

            # Extract the agent_name from the data
            agent_name = data.get('agent_name').lower()
            if not agent_name:
                LOG.warning("⚠️ Agent name not found in data.")
                return

            agent = self.agents.get(agent_name)
            if not agent:
                LOG.warning(
                    f"⚠️  No agent found with name: {agent_name}. Available agents: {list(self.agents.keys())}")
                return

            # Find the agent's reactions
            agent_reactions = self.reactions.get(agent_name)

            if agent_reactions:
                # Add the task_id and step_id to the data being sent to reactions
                data['current_task_id'] = self.current_task_id
                data['current_step_id'] = self.current_step_id

                # Logging the task and step IDs being added to data
                LOG.info(
                    f"📝  Adding task and step IDs to data for agent: {agent_name}. Task ID: {self.current_task_id}, Step ID: {self.current_step_id}")

                # Let the Reactions class handle the reaction
                reaction_method_name = f"on_{event}"
                reaction_method = getattr(
                    agent_reactions, reaction_method_name, agent_reactions.default_reaction)

                # Logging the reaction method that will be invoked
                LOG.info(
                    f"📝  Invoking reaction method: {reaction_method_name} for agent: {agent_name}")

                reaction_method(agent, data)

                # Logging after the reaction method has been invoked
                LOG.info(
                    f"📝  Reaction method {reaction_method_name} executed for agent: {agent_name}")

            else:
                LOG.warning(f"⚠️  No reactions found for agent: {agent_name}")

            # Notify all observers, including the ForgeAgent
            LOG.info(
                f"About to notify all observers with event: {event} and data: {data}")
            await self.notify_observers_async(event, data)   # Use await here
            LOG.info(f"All observers notified with event: {event}")

        except Exception as e:  # Catch any exception
            LOG.error(f"Error in receive_notification: {e}")

    async def notify_observers_async(self, event: str, data: Any = None):
        LOG.info(
            f"Notification event: {event} with data: {data} is being sent to observers.")
        # Assuming this is an async function
        await self.forge_agent.observer(event=event, data=data)
        LOG.info(
            f"Notification event: {event} has been sent to all observers.")
