"""
Test script demonstrating advanced usage of blockxai-chat

This script shows different ways to use the blockxai-chat package.
"""

import os
from dotenv import load_dotenv
from blockxai_chat.enhancer import enhance_prompt
from blockxai_chat.chatbot import Chatbot
from blockxai_chat.interface import run_interface, create_and_run

# Load environment variables
load_dotenv()

def test_method_1():
    """Method 1: The simplest way - one line of code"""
    print("Testing Method 1: One line of code")
    # You can provide an OpenAI API key as an argument, or enter it in the interface
    create_and_run("A customer service assistant for an e-commerce website.", openai_key=os.getenv("OPENAI_API_KEY"))

def test_method_2():
    """Method 2: Step by step approach with more control"""
    print("Testing Method 2: Step by step approach")
    
    # Step 1: Enhance a prompt
    simple_prompt = "A technical support assistant for software products."
    try:
        enhanced_prompt = enhance_prompt(simple_prompt)
        print(f"Enhanced prompt created: {len(enhanced_prompt)} characters")
    except Exception as e:
        print(f"Error enhancing prompt: {str(e)}")
        # Create a fallback prompt if enhancement fails
        enhanced_prompt = f"You are an AI assistant that {simple_prompt} Respond helpfully and accurately to user queries."
        print("Using fallback prompt instead.")
    
    # Step 2: Create a chatbot with the enhanced prompt
    # The API key can be provided now or later in the interface
    chatbot = Chatbot(
        system_prompt=enhanced_prompt,
        api_key=os.getenv("OPENAI_API_KEY"),  # This can be None
        model="gpt-3.5-turbo"
    )
    print("Chatbot created successfully")
    
    # Step 3: Run the interface with the chatbot
    print("Launching interface...")
    run_interface(chatbot)

def test_method_3():
    """Method 3: Using just the prompt with the interface"""
    print("Testing Method 3: Using just the prompt")
    
    # Just provide the prompt to the interface
    # It will handle the enhancement and chatbot creation
    # The API key will be entered in the interface
    print("Launching interface with just a prompt...")
    run_interface(prompt="A financial advisor that helps with investment decisions.")

if __name__ == "__main__":
    # Uncomment one of the methods below to test
    test_method_1()
    # test_method_2()
    # test_method_3()
