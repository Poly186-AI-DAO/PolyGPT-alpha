# main.py

from agents.core_agents import CoreAgent

def main():
    # Prompt the user for the initial message
    message = input("Enter the initial message for PolyGPT: ")

    # Create an instance of the CoreAgent with the provided message
    agent = CoreAgent(message)
    
    # Initiate a chat with the agent using the provided message
    agent.setup_group_chat()

if __name__ == "__main__":
    main()
