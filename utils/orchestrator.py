from typing import List, Optional, Tuple
import autogen

from enum import Enum, auto


class ConversationType(Enum):
    """
    Enum representing the various types of conversation patterns.

    - BROADCAST: A single agent sends a message to all other agents.
    - HIERARCHICAL: A hierarchical flow of communication, typically from a single sender to multiple receivers.
    - REQUEST_RESPOND: One agent sends a message and awaits a response from another agent.
    - TWO_WAY: A continuous back-and-forth conversation between two agents until a termination condition is met.
    - ROUND_ROBIN: Each agent takes turns communicating in a circular manner.
    - GROUP_BASED: A specified group of agents communicate in a particular order.
    - PROXY_BASED: One agent communicates on behalf of another agent.
    - STAR_NETWORK: A central agent communicates with all other agents.
    - ALL_TO_ALL: Every agent communicates with every other agent.
    """

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
    """
    A class to manage and facilitate various types of communication between conversable agents.

    Attributes:
    - name (str): The name of the orchestrator.
    - agents (List[autogen.ConversableAgent]): List of agents managed by the orchestrator.
    - messages (List[dict]): List of messages exchanged during conversations. Each message is a dictionary with a 'role' (sender/agent name) and 'content' (message content).
    - complete_keyword (str): Keyword signaling the completion of a conversation. Default is "APPROVED".
    - error_keyword (str): Keyword signaling an error in a conversation. Default is "ERROR".

    Raises:
    - Exception: If the orchestrator is initialized with fewer than two agents.
    """

    def __init__(self, name: str, agents: List[autogen.ConversableAgent]):
        """
        Initialize the Orchestrator with a name and a list of agents.

        Parameters:
        - name (str): The name of the orchestrator.
        - agents (List[autogen.ConversableAgent]): List of agents to be managed.
        """
        self.name = name
        self.agents = agents
        self.messages = []
        self.complete_keyword = "APPROVED"
        self.error_keyword = "ERROR"
        if len(self.agents) < 2:
            raise Exception("Orchestrator needs at least two agents")

    @property
    def total_agents(self) -> int:
        """
        Return the total number of agents managed by the orchestrator.

        Returns:
        - int: Total number of agents.
        """
        return len(self.agents)

    @property
    def latest_message(self) -> Optional[dict]:
        """
        Retrieve the most recent message exchanged in conversations.

        Returns:
        - dict or None: The latest message if present, else None. Message is a dictionary with a 'role' and 'content'.
        """
        if not self.messages:
            return None
        return self.messages[-1] if isinstance(self.messages[-1], dict) else {"role": "unknown", "content": self.messages[-1]}

    def add_message(self, message: dict):
        """
        Add a new message to the list of messages.

        Parameters:
        - message (dict): The message to add, containing a 'role' and 'content'.
        """
        self.messages.append(message)

    def basic_chat(self, agent_a: autogen.ConversableAgent, agent_b: autogen.ConversableAgent, message: str) -> dict:
        """
        Conduct a basic chat interaction between two agents. The process involves:
        1. `agent_a` sending a message to `agent_b`.
        2. `agent_b` generating and returning a reply.
        3. Storing the reply in the Orchestrator's messages list.

        Parameters:
        - agent_a (autogen.ConversableAgent): The sender agent who initiates the chat.
        - agent_b (autogen.ConversableAgent): The receiver agent who responds to the chat.
        - message (str): The message content to be sent from agent_a to agent_b.

        Returns:
        - dict: The reply from agent_b, structured as {"role": agent's name, "content": reply message}.
        """

        # Step 1: agent_a sends a message to agent_b.
        # The message is structured as a dictionary with content and the role (name) of the sender.
        agent_a.send({"content": message, "role": agent_a.name}, agent_b)

        # Step 2: agent_b generates a reply based on the message from agent_a.
        reply_content = agent_b.generate_reply(sender=agent_a)

        # Check the format of the reply. If it's a string, structure it as a dictionary.
        reply = {"role": agent_b.name, "content": reply_content} if isinstance(
            reply_content, str) else reply_content

        # Step 3: Add the reply to the Orchestrator's message list.
        self.add_message(reply)

        return reply

    def all_to_all_communication(self, initial_message: str):
        """
        Handles the all-to-all communication pattern.

        In this communication type, every agent communicates with every other agent.
        This means that if there are N agents, there will be N*(N-1) total communications.

        Parameters:
        - initial_message (str): The initial message to be passed among the agents.

        Usage example:
        ```
        orchestrator = Orchestrator(name="MainOrchestrator", agents=agents)
        orchestrator.start_conversation(
            pattern=ConversationType.ALL_TO_ALL,
            initial_message=message,
            starter_name="AgentName",  # Not used for ALL_TO_ALL but can be provided
            agent_order_names=["Agent1", "Agent2"]  # Not used for ALL_TO_ALL but can be provided
        )
        ```
        """
        message = initial_message
        for sender in self.agents:
            for receiver in self.agents:
                if sender != receiver:
                    reply = self.basic_chat(sender, receiver, message)
                    message = reply["content"]

    def star_network(self, central_agent: autogen.ConversableAgent, initial_message: str):
        """
        Handles the star network communication pattern.

        In this pattern, one agent (the central agent) communicates with all other agents.
        The central agent serves as a hub or central point of contact.

        Parameters:
        - central_agent (autogen.ConversableAgent): The central agent that communicates with all others.
        - initial_message (str): The initial message to be passed from the central agent.

        """
        message = initial_message
        for agent in self.agents:
            if agent != central_agent:
                reply = self.basic_chat(central_agent, agent, message)
                message = reply["content"]

    def proxy_based_communication(self, proxy: autogen.ConversableAgent, target: autogen.ConversableAgent, message: str):
        """
        Handles the proxy-based communication pattern.

        In this pattern, a proxy agent communicates with a target agent on behalf of another agent.

        Parameters:
        - proxy (autogen.ConversableAgent): The proxy agent that sends the message.
        - target (autogen.ConversableAgent): The target agent that receives the message.
        - message (str): The content of the message to be sent.

        """
        # Proxy sends the message on behalf of another agent
        reply = self.basic_chat(proxy, target, message)
        return reply

    def group_based_communication(self, starter: autogen.ConversableAgent, initial_message: str, agent_order: Optional[List[autogen.ConversableAgent]] = None):
        """
        Handles the group-based communication pattern.

        In this pattern, a starter agent communicates with other agents based on a specified order.
        If no specific order is provided, all agents are communicated with in their default order.

        Parameters:
        - starter (autogen.ConversableAgent): The agent initiating the communication.
        - initial_message (str): The initial message to be passed from the starter agent.
        - agent_order (Optional[List[autogen.ConversableAgent]]): An ordered list of agents for the communication. If not provided, default agent order is used.

        Usage:
        # Assuming the orchestrator and agents have been initialized
        orchestrator.group_based_communication(starter_agent, "Hello", [agent2, agent3, agent1])
        """
        if agent_order is None:
            agent_order = self.agents.copy()  # Use all agents in the default order
        message = initial_message
        for agent in agent_order:
            if agent != starter:
                reply = self.basic_chat(starter, agent, message)
                message = reply["content"]

    def two_way_communication(self, agent_a: autogen.ConversableAgent, agent_b: autogen.ConversableAgent, message: str):
        """
        Handles the two-way communication pattern.

        In this pattern, two agents converse back and forth until a termination condition, 
        represented by the `complete_keyword`, is encountered in a message.

        Parameters:
        - agent_a (autogen.ConversableAgent): The first agent involved in the conversation.
        - agent_b (autogen.ConversableAgent): The second agent involved in the conversation.
        - message (str): The initial message to start the conversation.

        Usage:
        # Assuming the orchestrator and agents have been initialized
        orchestrator.two_way_communication(agent1, agent2, "Initial message")
        """
        while True:  # Continue until a termination condition or keyword is found
            reply = self.basic_chat(agent_a, agent_b, message)
            if self.complete_keyword in reply["content"]:
                break
            agent_a, agent_b = agent_b, agent_a  # Swap roles
            message = reply["content"]

    def request_and_respond(self, sender: autogen.ConversableAgent, receiver: autogen.ConversableAgent, message: str):
        """
        Handles the request and respond communication pattern.

        In this simple pattern, one agent sends a message, and the other agent responds.

        Parameters:
        - sender (autogen.ConversableAgent): The agent sending the initial request.
        - receiver (autogen.ConversableAgent): The agent that responds to the request.
        - message (str): The content of the message or request to be sent.

        Usage:
        # Assuming the orchestrator and agents have been initialized
        orchestrator.request_and_respond(agent1, agent2, "Request message")
        """
        return self.basic_chat(sender, receiver, message)

    def hierarchical_communication(self, sender: autogen.ConversableAgent, receivers: List[autogen.ConversableAgent], message: str):
        """
        Handles the hierarchical communication pattern.

        In this pattern, a sender communicates with a list of receivers in order. 
        The communication halts when one of the receivers provides a reply.

        Parameters:
        - sender (autogen.ConversableAgent): The agent initiating the communication.
        - receivers (List[autogen.ConversableAgent]): List of agents that the sender communicates with.
        - message (str): The initial message sent by the sender.

        Usage:
        # Assuming the orchestrator and agents have been initialized
        orchestrator.hierarchical_communication(agent1, [agent2, agent3, agent4], "Hello")
        """
        for receiver in receivers:
            reply = self.basic_chat(sender, receiver, message)
            if reply:
                break

    def broadcast(self, sender: autogen.ConversableAgent, message: str):
        """
        Handles the broadcast communication pattern.

        In this pattern, a sender communicates the same message to all other agents.

        Parameters:
        - sender (autogen.ConversableAgent): The agent that broadcasts the message.
        - message (str): The content of the message to be broadcasted.

        Usage:
        # Assuming the orchestrator and agents have been initialized
        orchestrator.broadcast(agent1, "Broadcast message")
        """
        for agent in self.agents:
            if agent != sender:
                self.basic_chat(sender, agent, message)

    def round_robin(self, initial_message: str):
        """
        Handles the round robin communication pattern.

        In this pattern, agents communicate in a sequential order, passing messages in a 
        circular fashion. The first agent starts the conversation and then passes it to 
        the next agent until the last agent communicates with the first one.

        Parameters:
        - initial_message (str): The message to start the round robin communication.

        Usage:
        # Assuming the orchestrator and agents have been initialized
        orchestrator.round_robin("Starting message for round robin")
        """
        message = initial_message
        for agent in self.agents:
            reply = self.basic_chat(self.agents[0], agent, message)
            message = reply["content"]

    def group_based_communication(self, starter: autogen.ConversableAgent, initial_message: str, agent_order: Optional[List[autogen.ConversableAgent]] = None):
        """
        Handles the group-based communication pattern.

        Here, a starting agent communicates with a group of agents based on a specified 
        or default order. 

        Parameters:
        - starter (autogen.ConversableAgent): The agent initiating the group communication.
        - initial_message (str): The initial message to begin the group communication.
        - agent_order (Optional[List[autogen.ConversableAgent]]): Order in which agents communicate. 
        If not provided, the default order in the orchestrator's agent list is used.

        Usage:
        # Assuming the orchestrator and agents have been initialized
        orchestrator.group_based_communication(starting_agent, "Initial message for group chat", [agent2, agent3])
        """
        if agent_order is None:
            agent_order = self.agents.copy()
        message = initial_message
        for agent in agent_order:
            if agent != starter:
                reply = self.basic_chat(starter, agent, message)
                message = reply["content"]

    def proxy_based_communication(self, proxy: autogen.ConversableAgent, target: autogen.ConversableAgent, message: str):
        """
        Handles the proxy-based communication pattern.

        In this pattern, a proxy agent sends a message on behalf of another agent to the target.

        Parameters:
        - proxy (autogen.ConversableAgent): The agent acting as a proxy.
        - target (autogen.ConversableAgent): The agent receiving the message from the proxy.
        - message (str): The content of the message being relayed by the proxy.

        Usage:
        # Assuming the orchestrator and agents have been initialized
        orchestrator.proxy_based_communication(proxy_agent, target_agent, "Message through proxy")
        """
        return self.basic_chat(proxy, target, message)

    def star_network(self, central_agent: autogen.ConversableAgent, initial_message: str):
        """
        Handles the star network communication pattern.

        In this pattern, a central agent communicates with all other agents. Each agent 
        sends/receives messages only through this central agent.

        Parameters:
        - central_agent (autogen.ConversableAgent): The central agent that communicates with all other agents.
        - initial_message (str): The initial message used to start the communication.

        Usage:
        # Assuming the orchestrator and agents have been initialized
        orchestrator.star_network(central_hub_agent, "Message from central agent")
        """
        message = initial_message
        for agent in self.agents:
            if agent != central_agent:
                reply = self.basic_chat(central_agent, agent, message)
                message = reply["content"]

    def get_agent_by_name(self, name: str) -> Optional[autogen.ConversableAgent]:
        """
        Retrieve an agent based on its name.

        Parameters:
        - name (str): The name of the agent to retrieve.

        Returns:
        - autogen.ConversableAgent or None: The agent object if found, else None.

        Usage:
        # Assuming the orchestrator and agents have been initialized
        agent = orchestrator.get_agent_by_name("AgentName")
        """
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None

    def start_conversation(self, pattern: ConversationType, initial_message: str, **kwargs):
        """
        Initiates a conversation based on a specified communication pattern.

        Parameters:
        - pattern (ConversationType): The type of communication pattern to use.
        - initial_message (str): The initial message to start the conversation.
        - **kwargs: Additional keyword arguments depending on the communication pattern.
        For instance, `sender_name` or `agent_a_name` depending on the chosen pattern.

        Raises:
        - ValueError: If an unknown communication pattern is provided.

        Usage:
        # Assuming the orchestrator and agents have been initialized
        orchestrator.start_conversation(
            pattern=ConversationType.ALL_TO_ALL,
            initial_message="Initial message for all-to-all communication"
        )
        """

        """Initiates a conversation based on the specified pattern."""
        if pattern == ConversationType.BROADCAST:
            sender_name = kwargs.get("sender_name")
            sender = self.get_agent_by_name(sender_name)
            self.broadcast(sender, initial_message)

        elif pattern == ConversationType.HIERARCHICAL:
            sender_name = kwargs.get("sender_name")
            receivers_names = kwargs.get("receivers_names")
            receivers = [self.get_agent_by_name(
                name) for name in receivers_names]
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
            agent_order = [self.get_agent_by_name(
                name) for name in agent_order_names]
            self.group_based_communication(
                starter, initial_message, agent_order)

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
