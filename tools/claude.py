import os
from dotenv import load_dotenv
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

# Load .env file 
load_dotenv()

# Initialize API client
api_key = os.getenv('ANTHROPIC_API_KEY')
anthropic = Anthropic(api_key=api_key)

def generate_response(message):
  completion = anthropic.completions.create(
    model="claude-2",
    max_tokens_to_sample=300,
    prompt=f"{HUMAN_PROMPT}{message}{AI_PROMPT}",
  )

  return completion.completion

if __name__ == '__main__':
  # Get message from command line or user input
  import sys
  if len(sys.argv) > 1:
    message = sys.argv[1]
  else:
    message = input("Enter a prompt: ")
  
  response = generate_response(message)
  print(response)