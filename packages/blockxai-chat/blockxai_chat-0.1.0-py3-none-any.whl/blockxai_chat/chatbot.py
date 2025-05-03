"""
Chatbot module for blockxai-chat

This module provides the Chatbot class that interacts with OpenAI's GPT models
to generate responses based on the enhanced system prompt.
"""

import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Chatbot:
    """
    A chatbot class that uses OpenAI's GPT models to generate responses.
    
    Attributes:
        messages: List of conversation messages
        model: The OpenAI model to use
        client: OpenAI client instance
    """
    
    def __init__(self, system_prompt: str, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the chatbot with a system prompt.
        
        Args:
            system_prompt: The enhanced system prompt for the chatbot
            api_key: Optional OpenAI API key. If not provided, will use OPENAI_API_KEY from environment
            model: The OpenAI model to use (default: gpt-3.5-turbo)
        """
        self.messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
        self.model = model
        
        # Initialize OpenAI client
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OpenAI API key is required. Provide it as an argument or set OPENAI_API_KEY in your .env file.")
        self.client = OpenAI(api_key=key)
    
    def get_response(self, user_input: str, temperature: float = 0.7) -> str:
        """
        Get a response from the chatbot for the given user input.
        
        Args:
            user_input: The user's message
            temperature: Controls randomness in the response (0.0 to 1.0)
            
        Returns:
            The chatbot's response
        """
        # Add user message to conversation history
        self.messages.append({"role": "user", "content": user_input})
        
        try:
            # Generate response using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=temperature
            )
            
            # Extract and store the assistant's reply
            reply = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": reply})
            
            return reply
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            print(error_message)
            return error_message
    
    def clear_history(self, keep_system_prompt: bool = True) -> None:
        """
        Clear the conversation history.
        
        Args:
            keep_system_prompt: Whether to keep the system prompt (default: True)
        """
        if keep_system_prompt and self.messages:
            system_prompt = self.messages[0]
            self.messages = [system_prompt]
        else:
            self.messages = []
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the full conversation history.
        
        Returns:
            List of conversation messages
        """
        return self.messages
