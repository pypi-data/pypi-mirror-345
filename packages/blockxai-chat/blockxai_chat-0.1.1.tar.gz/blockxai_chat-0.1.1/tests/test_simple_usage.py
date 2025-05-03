"""
Test script demonstrating the simplest usage of blockxai-chat

This script shows how to create and run a chatbot with just two lines of code.
"""

import os
from dotenv import load_dotenv
from blockxai_chat.interface import create_and_run

# Load environment variables (optional)
load_dotenv()

# You can provide an OpenAI API key here, or enter it in the interface
openai_key = os.getenv("OPENAI_API_KEY","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")

print("Creating and running a chatbot with just two lines of code...")
print("The interface will open in your browser where you can enter your OpenAI API key.")

# Create and run a chatbot with a single line
create_and_run("A friendly assistant that helps users with their daily tasks.", openai_key=openai_key)
