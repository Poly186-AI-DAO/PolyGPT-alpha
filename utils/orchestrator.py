from typing import List, Optional, Tuple
import autogen

from enum import Enum, auto

class ConversationType(Enum):
    BROADCAST = auto()
    HIERARCHICAL = auto()
    REQUEST_RESPOND = auto()
    TWO_WAY = auto()
    ROUND_ROBIN = auto()
    GROUP_BASED = auto()
    PROXY_BASED = auto()
    STAR_NETWORK = auto()
    ALL_TO_ALL = auto()


class Orchestrator:
    def __init__(self, name: str, agents: List[autogen.ConversableAgent]):
        self.name = name
        self.agents = agents
        self.messages = []
        self.complete_keyword = "APPROVED"
        self.error_keyword = "ERROR"
        if len(self.agents) < 2:
            raise Exception("Orchestrator needs at least two agents")
    
    @property
    def total_agents(self):
        return len(self.agents)
    
    @property
    def latest_message(self) -> Optional[dict]:
        if not self.messages:
            return None
        return self.messages[-1] if isinstance(self.messages[-1], dict) else {"role": "unknown", "content": self.messages[-1]}
    
    def add_message(self, message):
        self.messages.append(message)
    
    def broadcast(self, sender: autogen.ConversableAgent, message: str):
        for agent in self.agents:
            if agent != sender:
                self.basic_chat(sender, agent, message)
    
    def hierarchical_communication(self, sender: autogen.ConversableAgent, receivers: List[autogen.ConversableAgent], message: str):
        for receiver in receivers:
            reply = self.basic_chat(sender, receiver, message)
            if reply:
                break
    
    def request_and_respond(self, sender: autogen.ConversableAgent, receiver: autogen.ConversableAgent, message: str):
        return self.basic_chat(sender, receiver, message)
    
    def two_way_communication(self, agent_a: autogen.ConversableAgent, agent_b: autogen.ConversableAgent, message: str):
        while True:  # Continue until a termination condition or keyword is found
            reply = self.basic_chat(agent_a, agent_b, message)
            if self.complete_keyword in reply["content"]:
                break
            agent_a, agent_b = agent_b, agent_a  # Swap roles
            message = reply["content"]

    def round_robin(self, initial_message: str):
        message = initial_message
        for agent in self.agents:
            reply = self.basic_chat(self.agents[0], agent, message)  # First agent starts the conversation
            message = reply["content"]

    def basic_chat(self, agent_a: autogen.ConversableAgent, agent_b: autogen.ConversableAgent, message: str) -> dict:
        agent_a.send({"content": message, "role": agent_a.name}, agent_b)
        reply = agent_b.generate_reply(sender=agent_a)
        reply = {"role": agent_b.name, "content": reply} if isinstance(reply, str) else reply
        self.add_message(reply)
        return reply

    def group_based_communication(self, starter: autogen.ConversableAgent, initial_message: str, agent_order: Optional[List[autogen.ConversableAgent]] = None):
        if agent_order is None:
            agent_order = self.agents.copy()  # Use all agents in the default order
        message = initial_message
        for agent in agent_order:
            if agent != starter:
                reply = self.basic_chat(starter, agent, message)
                message = reply["content"]

    def proxy_based_communication(self, proxy: autogen.ConversableAgent, target: autogen.ConversableAgent, message: str):
        # Proxy sends the message on behalf of another agent
        reply = self.basic_chat(proxy, target, message)
        return reply

    def star_network(self, central_agent: autogen.ConversableAgent, initial_message: str):
        message = initial_message
        for agent in self.agents:
            if agent != central_agent:
                reply = self.basic_chat(central_agent, agent, message)
                message = reply["content"]

    def all_to_all_communication(self, initial_message: str):
        message = initial_message
        for sender in self.agents:
            for receiver in self.agents:
                if sender != receiver:
                    reply = self.basic_chat(sender, receiver, message)
                    message = reply["content"]

    def get_agent_by_name(self, name: str) -> Optional[autogen.ConversableAgent]:
        """Retrieve an agent by its name."""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None


    def start_conversation(self, pattern: ConversationType, initial_message: str, **kwargs):
        """Initiates a conversation based on the specified pattern."""
        if pattern == ConversationType.BROADCAST:
            sender_name = kwargs.get("sender_name")
            sender = self.get_agent_by_name(sender_name)
            self.broadcast(sender, initial_message)

        elif pattern == ConversationType.HIERARCHICAL:
            sender_name = kwargs.get("sender_name")
            receivers_names = kwargs.get("receivers_names")
            receivers = [self.get_agent_by_name(name) for name in receivers_names]
            self.hierarchical_communication(sender, receivers, initial_message)

        elif pattern == ConversationType.REQUEST_RESPOND:
            sender_name = kwargs.get("sender_name")
            receiver_name = kwargs.get("receiver_name")
            sender = self.get_agent_by_name(sender_name)
            receiver = self.get_agent_by_name(receiver_name)
            self.request_and_respond(sender, receiver, initial_message)

        elif pattern == ConversationType.TWO_WAY:
            agent_a_name = kwargs.get("agent_a_name")
            agent_b_name = kwargs.get("agent_b_name")
            agent_a = self.get_agent_by_name(agent_a_name)
            agent_b = self.get_agent_by_name(agent_b_name)
            self.two_way_communication(agent_a, agent_b, initial_message)

        elif pattern == ConversationType.ROUND_ROBIN:
            self.round_robin(initial_message)

        elif pattern == ConversationType.GROUP_BASED:
            starter_name = kwargs.get("starter_name")
            agent_order_names = kwargs.get("agent_order_names", [])
            starter = self.get_agent_by_name(starter_name)
            agent_order = [self.get_agent_by_name(name) for name in agent_order_names]
            self.group_based_communication(starter, initial_message, agent_order)

        elif pattern == ConversationType.PROXY_BASED:
            proxy_name = kwargs.get("proxy_name")
            target_name = kwargs.get("target_name")
            proxy = self.get_agent_by_name(proxy_name)
            target = self.get_agent_by_name(target_name)
            self.proxy_based_communication(proxy, target, initial_message)

        elif pattern == ConversationType.STAR_NETWORK:
            central_agent_name = kwargs.get("central_agent_name")
            central_agent = self.get_agent_by_name(central_agent_name)
            self.star_network(central_agent, initial_message)

        elif pattern == ConversationType.ALL_TO_ALL:
            self.all_to_all_communication(initial_message)

        else:
            raise ValueError(f"Unknown communication pattern: {pattern}")