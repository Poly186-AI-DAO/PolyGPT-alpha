from enum import Enum, auto
import logging
import autogen
from typing import List, Optional, Callable

from utils.autogen.chat_type import ChatType



# Initialize the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageRole(Enum):
    REGULAR = auto()
    SYSTEM = auto()
    ERROR = auto()


class AgentStatus(Enum):
    ONLINE = auto()
    OFFLINE = auto()
    BUSY = auto()  # New Status

class ChatHandler:
    def __init__(self, chat_manager):
        self.chat_manager = chat_manager
        self.agents = chat_manager.get_agents()
        self.agent_priorities = {agent.name: 1 for agent in self.agents}
        self.agent_statuses = {
            agent.name: AgentStatus.ONLINE for agent in self.agents}
        self.chat_history = []
        self.admin_agent = None
        self.event_hooks = {
            'on_message_send': [],
            'on_message_receive': [],
            'on_chat_end': []
        }

    def conduct_chat(self, chat_type: ChatType, *args, **kwargs) -> Optional[dict]:
        chat_method_mapping = {
            ChatType.BROADCAST: self.broadcast,
            ChatType.HIERARCHICAL: self.hierarchical_communication,
            ChatType.REQUEST_RESPOND: self.request_and_respond,
            ChatType.TWO_WAY: self.two_way_communication,
            ChatType.GROUP_BASED: self.group_based_communication
        }

        if chat_type not in chat_method_mapping:
            raise ValueError(f"Unsupported chat type: {chat_type}")

        return chat_method_mapping[chat_type](*args, **kwargs)

    def broadcast(self, sender: autogen.ConversableAgent, message: str, include_sender=False):
        # Highest priority first
        for agent in sorted(self.agents, key=lambda a: self.agent_priorities[a.name], reverse=True):
            if not include_sender and agent == sender:
                continue
            self.basic_chat(sender, agent, message)

    def hierarchical_communication(self, sender: autogen.ConversableAgent, receivers: List[autogen.ConversableAgent], message: str, termination_keyword=None):
        # Highest priority first
        for receiver in sorted(receivers, key=lambda a: self.agent_priorities[a.name], reverse=True):
            reply = self.basic_chat(sender, receiver, message)
            if termination_keyword and termination_keyword in reply["content"]:
                break

    def request_and_respond(self, sender: autogen.ConversableAgent, receiver: autogen.ConversableAgent, message: str):
        return self.basic_chat(sender, receiver, message)

    def two_way_communication(self, agents: List[autogen.ConversableAgent], initial_message: str, termination_keyword: str, max_iterations: int = 10):
        """Conduct a two-way communication until termination keyword is found or max iterations are reached."""
        message = initial_message
        agent_count = len(agents)
        i = 0
        iteration = 0
        while iteration < max_iterations:
            reply = self.basic_chat(
                agents[i], agents[(i + 1) % agent_count], message)
            if termination_keyword in reply["content"]:
                self.event_hooks['on_chat_end'](
                    agents[i], agents[(i + 1) % agent_count])
                break
            message = reply["content"]
            i = (i + 1) % agent_count
            iteration += 1
        if iteration == max_iterations:
            logger.warning(
                "Two-way communication reached maximum iterations without encountering the termination keyword.")

    def group_based_communication(self, starter: autogen.ConversableAgent, initial_message: str, agent_order: Optional[List[autogen.ConversableAgent]] = None):
        if agent_order is None:
            agent_order = sorted(
                self.agents, key=lambda a: self.agent_priorities[a.name], reverse=True)
        message = initial_message
        for agent in agent_order:
            if agent != starter:
                reply = self.basic_chat(starter, agent, message)
                message = reply["content"]

    def basic_chat(self, agent_a: autogen.ConversableAgent, agent_b: autogen.ConversableAgent, message: str, role: MessageRole = MessageRole.REGULAR) -> dict:
        if self.agent_statuses[agent_b.name] == AgentStatus.OFFLINE:
            return {'role': agent_b.name, 'content': 'Agent is offline', 'type': MessageRole.ERROR}

        for callback in self.event_hooks['on_message_send']:
            callback(agent_a, agent_b, message)

        agent_a.send(
            {"content": message, "role": agent_a.name, "type": role}, agent_b)
        reply_content = agent_b.generate_reply(sender=agent_a)
        reply = {"role": agent_b.name, "content": reply_content, "type": role}

        self.chat_manager.add_message(reply)
        self.chat_history.append(reply)

        for callback in self.event_hooks['on_message_receive']:
            callback(agent_a, agent_b, reply)

        return reply

    # Utility methods
    def add_agent(self, agent: autogen.ConversableAgent):
        if agent not in self.agents:
            self.agents.append(agent)
            self.agent_priorities[agent.name] = 1  # Default priority
            # Default status
            self.agent_statuses[agent.name] = AgentStatus.ONLINE
        else:
            raise ValueError(f"Agent {agent.name} already exists")

    def remove_agent(self, agent_name: str):
        agent_to_remove = self.get_agent_by_name(agent_name)
        if agent_to_remove:
            self.agents.remove(agent_to_remove)
            del self.agent_priorities[agent_name]
            del self.agent_statuses[agent_name]
        else:
            raise ValueError(f"Agent {agent_name} not found")

    def get_agent_by_name(self, name: str) -> autogen.ConversableAgent:
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None

    def reset_chat(self):
        self.chat_history = []

    def set_admin_agent(self, agent: autogen.ConversableAgent):
        self.admin_agent = agent

    # Assume a next_agent logic based on some dynamic rules or just the next in list for now
    def next_agent(self, current_agent: autogen.ConversableAgent) -> autogen.ConversableAgent:
        current_index = self.agents.index(current_agent)
        return self.agents[(current_index + 1) % len(self.agents)]

    # The event hook registration
    def add_event_hook(self, event_name: str, callback: Callable):
        if event_name in self.event_hooks:
            self.event_hooks[event_name].append(callback)
        else:
            raise ValueError(f"Unsupported event: {event_name}")

    # Setting agent priority and status
    def set_agent_priority(self, agent_name: str, priority: int):
        if agent_name in self.agent_priorities:
            self.agent_priorities[agent_name] = priority
        else:
            raise ValueError(f"Agent {agent_name} not found")

    def set_agent_status(self, agent_name: str, status: AgentStatus):
        if agent_name in self.agent_statuses:
            self.agent_statuses[agent_name] = status
        else:
            raise ValueError(f"Agent {agent_name} not found")
