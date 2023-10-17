# main.py

from agents.core.core_agents import CoreAgent

def main():
    # Prompt the user for the initial message
    message = input("Enter the initial message for the agent: ")

    # Create an instance of the CoreAgent
    agent = CoreAgent()
    
    # Initiate a chat with the agent using the provided message
    agent.initiate_chat(message)

if __name__ == "__main__":
    main()
