from typing import Any
from agents.agents_initializer import AgentInitializer
from utils.autogen_monitor import AutogenMonitor

from utils.observer import Observable
from utils.poly_logger import PolyLogger
from utils.reaction import Reactions

LOG = PolyLogger(__name__)


class PolyGPTAgents(Observable):
    def __init__(self, database, workspace):
        super().__init__()
        self.agent_monitors = []
        self.forge_agent = None
        self.database = database
        self.workspace = workspace
        self.reactions = {}

        self._initialize_agents()

    def _initialize_agents(self):
        self.agent_initializer = AgentInitializer(
            self.database, self.workspace)
        self.agents = self.agent_initializer.agents
        self.groupchat = self.agent_initializer.groupchat
        self.manager = self.agent_initializer.manager

        for agent_name, agent in self.agents.items():
            if agent_name not in self.reactions:
                self.reactions[agent_name] = Reactions(
                    agent, self.database, self.workspace)

            agent_monitor = AutogenMonitor(
                agent, self, self.groupchat, self.manager)

            for event_name in agent_monitor.default_monitored_methods:
                agent_monitor.add_observer(self.receive_notification, event=event_name)

            self.agent_monitors.append(agent_monitor)

    def set_forge_agent(self, agent):
        self.forge_agent = agent

    def start_chat(self, user_input):
        self.agent_initializer.initiate_chat(user_input)

    async def receive_notification(self, event: str, data: Any):
        try:
            agent_name = data.get('agent_name').lower()
            if not agent_name:
                return

            agent = self.agents.get(agent_name)
            if not agent:
                return

            agent_reactions = self.reactions.get(agent_name)

            if agent_reactions:
                reaction_method_name = f"on_{event}"
                reaction_method = getattr(
                    agent_reactions, reaction_method_name, agent_reactions.default_reaction)

                reaction_method(agent, data)

            await self.notify_observers_async(event, data)

        except Exception as e:
            LOG.error(f"Error in receive_notification: {e}")

    async def notify_observers_async(self, event: str, data: Any = None):
        await super().notify_observers_async(event, data)
