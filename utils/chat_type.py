from enum import Enum, auto


class ChatType(Enum):

    """
    The ChatType enum represents common patterns of communication flow between
    agents in a conversation.

    BROADCAST:
      A one-to-many pattern where a single sender agent transmits a message 
      to all other agents. Useful for disseminating information efficiently.

    HIERARCHICAL: 
      A one-to-many pattern with a hierarchical, tree-like flow from one sender 
      to multiple receivers. Can encode command flows or task delegation.  

    REQUEST_RESPOND:
      A request-response pair between two agents. One agent queries another
      and receives a reply. Models question-answering dialogues.

    TWO_WAY: 
      An extended back-and-forth conversation between two agents. Agents alternate
      roles as sender and receiver until a termination condition is met. Allows
      natural free-flowing dialogues.

    GROUP_BASED:
      Agents are divided into groups with communications occurring between groups.
      Useful for modeling factions, teams, or other clusters of agents.
    """

    BROADCAST = auto()

    HIERARCHICAL = auto()

    REQUEST_RESPOND = auto()

    TWO_WAY = auto()

    GROUP_BASED = auto()
