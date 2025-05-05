# askharsha

A minimal chatbot module for interacting with end user returning clean plain-text responses.

## Installation

```bash
pip install askharsha

## Usage 
from askharsha import Chatbot

bot = Chatbot(api_key="YOUR_GEMINI_API_KEY")
response = bot.ask("What is 5*2 and 5**2?")
print(response)

## Output 
5*2 is 10  
5**2 is 25  


