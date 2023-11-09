from typing import List, Optional
import autogen
from utils.chat_handler import ChatHandler
from utils.chat_type import ChatType


class ChatManager:
    """
    A class to manage and facilitate various types of communication between conversable agents.
    Attributes:
    - name (str): The name of the orchestrator.
    - agents (List[autogen.ConversableAgent]): List of agents managed by the orchestrator.
    - messages (List[dict]): List of messages exchanged during conversations.
    """

    def __init__(self,
                 name: str,
                 agents: List[autogen.ConversableAgent],
                 max_rounds: int = 10):
        self.name = name
        self.agents = agents
        self.messages = []
        self.chat_handler = ChatHandler(self)
        self.max_rounds = max_rounds
        if len(self.agents) < 2:
            raise Exception("ChatManager needs at least two agents")

    @property
    def latest_message(self) -> Optional[dict]:
        """Retrieve the most recent message exchanged in conversations."""
        if not self.messages:
            return None
        return self.messages[-1]

    def add_message(self, message: dict):
        """Add a new message to the list of messages."""
        self.messages.append(message)

    def get_agent_by_name(self, name: str) -> Optional[autogen.ConversableAgent]:
        """Retrieve an agent based on its name."""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return ValueError(f"No agent found with name: {name}")

    def get_agents(self) -> List[autogen.ConversableAgent]:
        """Returns the list of agents managed by the ChatManager."""
        return self.agents

    def start_conversation(self, pattern: ChatType, initial_message: str, **kwargs):
        """Initiates a conversation based on a specified communication pattern."""
        if pattern == ChatType.BROADCAST:
            sender_name = kwargs.get("sender_name")
            sender = self.get_agent_by_name(sender_name)
            self.chat_handler.broadcast(sender, initial_message)

        elif pattern == ChatType.HIERARCHICAL:
            sender_name = kwargs.get("sender_name")
            receivers_names = kwargs.get("receivers_names", [])
            receivers = [self.get_agent_by_name(
                name) for name in receivers_names]
            sender = self.get_agent_by_name(sender_name)
            self.chat_handler.hierarchical_communication(
                sender, receivers, initial_message)

        elif pattern == ChatType.REQUEST_RESPOND:
            sender_name = kwargs.get("sender_name")
            receiver_name = kwargs.get("receiver_name")
            sender = self.get_agent_by_name(sender_name)
            receiver = self.get_agent_by_name(receiver_name)
            self.chat_handler.request_and_respond(
                sender, receiver, initial_message)

        elif pattern == ChatType.TWO_WAY:
            agents_names = kwargs.get("agents_names")
            agents = [self.get_agent_by_name(name) for name in agents_names]
            self.chat_handler.two_way_communication(
                agents, initial_message, self.max_rounds)

        elif pattern == ChatType.GROUP_BASED:
            starter_name = kwargs.get("starter_name")
            agent_order_names = kwargs.get("agent_order_names", [])
            starter = self.get_agent_by_name(starter_name)
            agent_order = [self.get_agent_by_name(
                name) for name in agent_order_names]
            self.chat_handler.group_based_communication(
                starter, initial_message, agent_order)

        else:
            raise ValueError(f"Unknown communication pattern: {pattern}")
