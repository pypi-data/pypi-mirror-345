"""
Enhancer module for blockxai-chat

This module uses Google's Gemini API to enhance simple prompts into comprehensive
system prompts for chatbot applications.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Preset API key for developers
DEFAULT_GEMINI_API_KEY = "AIzaSyB4vOlk6NWBsCd9fzUDUNiL1uXOd-mccVk"

# Configure Gemini API
def configure_gemini(api_key: Optional[str] = None):
    """Configure the Gemini API with the provided key or from environment variables."""
    key = api_key or os.getenv("GEMINI_API_KEY") or DEFAULT_GEMINI_API_KEY
    genai.configure(api_key=key)

def enhance_prompt(user_prompt: str, api_key: Optional[str] = None) -> str:
    """
    Enhance a simple user prompt into a comprehensive system prompt using Gemini API.
    
    Args:
        user_prompt: The simple prompt provided by the user
        api_key: Optional Gemini API key. If not provided, will use GEMINI_API_KEY from environment
               or the preset default key
        
    Returns:
        Enhanced system prompt for the chatbot
    """
    # Configure Gemini with API key (custom, environment, or default)
    configure_gemini(api_key)
    
    # Create enhancement instruction
    enhancement_prompt = f"""
    Transform the following simple prompt into a comprehensive, detailed system prompt for an AI chatbot.
    The enhanced prompt should:
    1. Define the chatbot's personality, tone, and communication style
    2. Specify the chatbot's knowledge domains and limitations
    3. Include guidelines for handling different types of user queries
    4. Establish boundaries for what the chatbot should and shouldn't do
    5. Provide examples of ideal responses when relevant
    
    Simple prompt: "{user_prompt}"
    
    Enhanced system prompt:
    """
    
    # Generate enhanced prompt using Gemini
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(enhancement_prompt)
        enhanced_prompt = response.text.strip()
        
        # Add fallback if the response is empty
        if not enhanced_prompt:
            return f"You are an AI assistant that {user_prompt} Respond helpfully and accurately to user queries."
            
        return enhanced_prompt
    except Exception as e:
        # Provide a fallback in case of API errors
        print(f"Error enhancing prompt with Gemini: {str(e)}")
        return f"You are an AI assistant that {user_prompt} Respond helpfully and accurately to user queries."
