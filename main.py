import os
from utils.poly_logger import PolyLogger
from agents.polygpt import PolyGPTAgents
from utils.sqlalchemy import PolyDatabase
from utils.workspace import LocalWorkspace

LOG = PolyLogger(__name__)

def main():
    # Prompt the user for the initial message
    message = input("Enter the initial message for PolyGPT: ")

    # Assuming you have a database and workspace already set up

    database_name = os.getenv("DATABASE_STRING")
    workspace = LocalWorkspace(os.getenv("AGENT_WORKSPACE"))
    database = PolyDatabase(database_name, debug_enabled=False)

    # Create an instance of the PolyGPTAgents with the provided database and workspace
    poly_gpt_agent = PolyGPTAgents(database, workspace)

    # Initiate a chat with the PolyGPTAgents using the provided message
    poly_gpt_agent.start_chat(user_input=message)

if __name__ == "__main__":
    main()
