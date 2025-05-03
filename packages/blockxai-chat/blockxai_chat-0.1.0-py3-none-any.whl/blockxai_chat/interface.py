"""
Interface module for blockxai-chat

This module provides a Streamlit-based interface for interacting with the chatbot.
"""

import streamlit as st
from typing import Optional
from blockxai_chat.enhancer import enhance_prompt
from blockxai_chat.chatbot import Chatbot

def run_interface(chatbot: Optional[Chatbot] = None):
    """
    Run the Streamlit interface for the chatbot.
    
    Args:
        chatbot: Optional pre-initialized Chatbot instance
    """
    st.set_page_config(
        page_title="BlockXAI Chat",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("BlockXAI Chat")
    st.subheader("Create AI chatbots with a single prompt")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # API keys input
        st.markdown("**API Keys**")
        openai_key = st.text_input("OpenAI API Key", type="password", help="Your OpenAI API key")
        
        # Gemini API key with note about preset key
        gemini_key_expander = st.expander("Gemini API Key (Optional)")
        with gemini_key_expander:
            st.markdown("*A preset Gemini API key is included with this package. You only need to provide your own key if you want to use a different one.*")
            gemini_key = st.text_input("Your Gemini API Key", type="password", help="Your Google Gemini API key (optional)")

        
        # Model selection
        model = st.selectbox(
            "OpenAI Model",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            index=0,
            help="Select the OpenAI model to use"
        )
        
        # Temperature slider
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Controls randomness in the response (0.0 to 1.0)"
        )
        
        # Clear conversation button
        if "chatbot" in st.session_state and st.button("Clear Conversation"):
            st.session_state.chatbot.clear_history()
            st.session_state.messages = []
            st.experimental_rerun()
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Use provided chatbot or create a new one
    if chatbot and "chatbot" not in st.session_state:
        st.session_state.chatbot = chatbot
        st.session_state.setup_complete = True
    
    # Chatbot setup
    if "setup_complete" not in st.session_state:
        st.markdown("### Create Your Chatbot")
        
        user_prompt = st.text_area(
            "Enter a simple prompt to define your chatbot:",
            placeholder="Example: A friendly assistant that helps users with their daily tasks.",
            height=100
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            create_button = st.button("Create Chatbot", type="primary")
        
        if create_button and user_prompt:
            with st.spinner("Enhancing prompt with Gemini..."):
                try:
                    enhanced_prompt = enhance_prompt(user_prompt, api_key=gemini_key)
                    
                    with st.expander("View Enhanced System Prompt"):
                        st.markdown(enhanced_prompt)
                    
                    # Initialize chatbot
                    st.session_state.chatbot = Chatbot(
                        system_prompt=enhanced_prompt,
                        api_key=openai_key,
                        model=model
                    )
                    
                    st.session_state.setup_complete = True
                    st.success("Chatbot created successfully!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error creating chatbot: {str(e)}")
    
    # Chat interface
    if "setup_complete" in st.session_state:
        # User input
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.chatbot.get_response(user_input, temperature=temperature)
                    st.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})


def create_and_run(prompt: str, gemini_key: Optional[str] = None, openai_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
    """
    Create a chatbot from a prompt and run the interface.
    
    This is a convenience function for developers who want to create and run a chatbot in one line.
    
    Args:
        prompt: The simple prompt to enhance
        gemini_key: Optional Gemini API key
        openai_key: Optional OpenAI API key
        model: The OpenAI model to use
    """
    # Enhance the prompt
    enhanced_prompt = enhance_prompt(prompt, api_key=gemini_key)
    
    # Create the chatbot
    chatbot = Chatbot(enhanced_prompt, api_key=openai_key, model=model)
    
    # Run the interface
    run_interface(chatbot)
