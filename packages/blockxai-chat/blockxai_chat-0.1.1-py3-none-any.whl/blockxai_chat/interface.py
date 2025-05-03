"""
Interface module for blockxai-chat

This module provides a Gradio-based interface for interacting with the chatbot.
"""

import os
import gradio as gr
from typing import Optional, List, Dict, Tuple, Callable
from dotenv import load_dotenv
from blockxai_chat.enhancer import enhance_prompt
from blockxai_chat.chatbot import Chatbot

# Load environment variables
load_dotenv()

class ChatbotInterface:
    """A class to manage the chatbot and its interface"""
    
    def __init__(self):
        """Initialize the chatbot interface"""
        self.chatbot = None
        self.history = []
        self.enhanced_prompt = ""
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.7
    
    def enhance_user_prompt(self, prompt: str, gemini_key: Optional[str] = None) -> str:
        """Enhance a user prompt using Gemini"""
        try:
            enhanced = enhance_prompt(prompt, api_key=gemini_key)
            self.enhanced_prompt = enhanced
            return f"✅ Prompt enhanced successfully! Your chatbot is ready to use."
        except Exception as e:
            error_message = str(e)
            fallback_prompt = f"You are an AI assistant that {prompt} Respond helpfully and accurately to user queries."
            self.enhanced_prompt = fallback_prompt
            return f"⚠️ Error enhancing prompt: {error_message}\n\nUsing fallback prompt instead."
    
    def initialize_chatbot(self, openai_key: Optional[str] = None, model: str = "gpt-3.5-turbo") -> str:
        """Initialize the chatbot with the enhanced prompt"""
        try:
            if not self.enhanced_prompt:
                return "⚠️ Please enhance a prompt first."
            
            # Create chatbot with or without API key
            self.chatbot = Chatbot(
                system_prompt=self.enhanced_prompt,
                api_key=openai_key or self.openai_key,
                model=model
            )
            
            self.model = model
            
            # Set API key if provided
            if openai_key:
                self.openai_key = openai_key
                self.chatbot.set_api_key(openai_key)
                
            return "✅ Chatbot initialized successfully!"
        except Exception as e:
            return f"⚠️ Error initializing chatbot: {str(e)}"
    
    def chat(self, user_message: str, temperature: Optional[float] = None) -> str:
        """Get a response from the chatbot"""
        if not self.chatbot:
            return "⚠️ Please initialize the chatbot first."
        
        try:
            temp = temperature if temperature is not None else self.temperature
            response = self.chatbot.get_response(user_message, temperature=temp)
            self.history.append((user_message, response))
            return response
        except Exception as e:
            return f"⚠️ Error: {str(e)}"
    
    def clear_history(self) -> None:
        """Clear the chat history"""
        if self.chatbot:
            self.chatbot.clear_history()
        self.history = []


def create_gradio_interface(chatbot_interface: Optional[ChatbotInterface] = None) -> gr.Blocks:
    """Create a Gradio interface for the chatbot"""
    if chatbot_interface is None:
        chatbot_interface = ChatbotInterface()
    
    with gr.Blocks(title="BlockXAI Chat") as interface:
        gr.Markdown("# BlockXAI Chat")
        gr.Markdown("### Create AI chatbots with a single prompt")
        
        # API Key Input at the top level for better visibility
        with gr.Accordion("API Key Setup", open=True):
            openai_key = gr.Textbox(
                placeholder="Enter your OpenAI API key to get started",
                label="OpenAI API Key",
                type="password",
                value=os.getenv("OPENAI_API_KEY", ""),
                info="Required to generate chatbot responses"
            )
            
            api_key_submit = gr.Button("Save API Key", variant="primary")
            api_key_status = gr.Markdown("")
            
            # Event handler for API key submission
            def save_api_key(key):
                if not key:
                    return "⚠️ Please enter an OpenAI API key"
                
                chatbot_interface.openai_key = key
                
                # If chatbot already exists, update its API key
                if chatbot_interface.chatbot:
                    success = chatbot_interface.chatbot.set_api_key(key)
                    if not success:
                        return "⚠️ Failed to set API key for chatbot"
                        
                return "✅ API key saved successfully!"
            
            api_key_submit.click(save_api_key, openai_key, api_key_status)
        
        with gr.Tab("Chat"):
            chatbot = gr.Chatbot(height=500, show_copy_button=True)
            
            with gr.Row():
                with gr.Column(scale=8):
                    msg = gr.Textbox(
                        placeholder="Type your message here...",
                        container=False,
                        scale=8,
                        show_label=False
                    )
                with gr.Column(scale=1):
                    submit_btn = gr.Button("Send", variant="primary")
            
            with gr.Row():
                clear_btn = gr.Button("Clear Conversation")
                temperature_slider = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=0.7,
                    step=0.1,
                    label="Temperature",
                    info="Controls randomness in the response (0.0 to 1.0)"
                )
        
        with gr.Tab("Setup"):
            with gr.Group():
                gr.Markdown("### 1. Define your chatbot")
                user_prompt = gr.Textbox(
                    placeholder="Example: A friendly assistant that helps users with their daily tasks.",
                    label="Enter a simple prompt to define your chatbot:",
                    lines=3
                )
                enhance_btn = gr.Button("Enhance Prompt", variant="primary")
                enhance_output = gr.Markdown()
            
            with gr.Group():
                gr.Markdown("### 2. Configure your chatbot")
                with gr.Accordion("Advanced Settings", open=False):
                    # OpenAI key is now at the top level, so we just reference it here
                    gemini_key = gr.Textbox(
                        placeholder="A preset Gemini API key is included with this package",
                        label="Gemini API Key (Optional)",
                        type="password",
                        info="You only need to provide your own key if you want to use a different one."
                    )
                    model_dropdown = gr.Dropdown(
                        choices=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                        label="OpenAI Model",
                        value="gpt-3.5-turbo"
                    )
                
                initialize_btn = gr.Button("Initialize Chatbot")
                initialize_output = gr.Markdown()
        
        # Define event handlers
        def user_message(user_input, history):
            return "", history + [[user_input, None]]
        
        def bot_response(history):
            user_input = history[-1][0]
            bot_message = chatbot_interface.chat(user_input)
            history[-1][1] = bot_message
            return history
        
        msg.submit(user_message, [msg, chatbot], [msg, chatbot]).then(
            bot_response, chatbot, chatbot
        )
        
        submit_btn.click(user_message, [msg, chatbot], [msg, chatbot]).then(
            bot_response, chatbot, chatbot
        )
        
        clear_btn.click(
            lambda: ([], None),
            None,
            [chatbot, enhance_output],
            queue=False
        ).then(lambda: chatbot_interface.clear_history())
        
        temperature_slider.change(
            lambda temp: setattr(chatbot_interface, 'temperature', temp) or None,
            temperature_slider,
            None
        )
        
        enhance_btn.click(
            chatbot_interface.enhance_user_prompt,
            [user_prompt, gemini_key],
            enhance_output
        )
        
        # Use the API key from the top level for initialization
        initialize_btn.click(
            lambda model: chatbot_interface.initialize_chatbot(chatbot_interface.openai_key, model),
            [model_dropdown],
            initialize_output
        )
        
        # Add footer
        gr.Markdown("---")
        gr.Markdown("### Developed by BlockXAI")
    
    return interface


def run_interface(chatbot: Optional[Chatbot] = None, prompt: Optional[str] = None) -> None:
    """
    Run the Gradio interface for the chatbot.
    
    Args:
        chatbot: Optional pre-initialized Chatbot instance
        prompt: Optional simple prompt to create a chatbot if none is provided
    """
    interface = ChatbotInterface()
    
    # If a chatbot is provided, use it
    if chatbot:
        interface.chatbot = chatbot
        interface.enhanced_prompt = chatbot.messages[0]["content"] if chatbot.messages else ""
    
    # If a prompt is provided but no chatbot, enhance the prompt
    elif prompt:
        interface.enhance_user_prompt(prompt)
        if interface.enhanced_prompt:
            interface.initialize_chatbot()
    
    # Create and launch the Gradio interface
    gradio_interface = create_gradio_interface(interface)
    gradio_interface.launch(share=False)


def create_and_run(prompt: str, gemini_key: Optional[str] = None, openai_key: Optional[str] = None, model: str = "gpt-3.5-turbo") -> None:
    """
    Create a chatbot from a prompt and run the interface.
    
    This is a convenience function for developers who want to create and run a chatbot in one line.
    The OpenAI API key can be provided as an argument, through environment variables,
    or directly in the interface.
    
    Args:
        prompt: The simple prompt to enhance
        gemini_key: Optional Gemini API key
        openai_key: Optional OpenAI API key
        model: The OpenAI model to use
    """
    try:
        print("Enhancing prompt with Gemini...")
        # Try to enhance the prompt, but handle errors gracefully
        try:
            enhanced_prompt = enhance_prompt(prompt, api_key=gemini_key)
            print("Prompt enhanced successfully!")
        except Exception as e:
            print(f"Error enhancing prompt: {str(e)}")
            # Create a fallback prompt if enhancement fails
            enhanced_prompt = f"You are an AI assistant that {prompt} Respond helpfully and accurately to user queries."
            print("Using fallback prompt instead.")
        
        # Initialize the interface
        interface = ChatbotInterface()
        interface.enhanced_prompt = enhanced_prompt
        
        # If OpenAI key is provided, use it
        if openai_key:
            interface.openai_key = openai_key
            interface.initialize_chatbot(openai_key, model)
            print("Chatbot initialized with provided API key.")
        else:
            # Create the chatbot without an API key
            interface.initialize_chatbot(None, model)
            print("No OpenAI API key provided. You'll need to enter it in the interface.")
        
        # Create and launch the Gradio interface
        print("Launching Gradio interface...")
        gradio_interface = create_gradio_interface(interface)
        gradio_interface.launch(share=False)
    except Exception as e:
        print(f"Error: {str(e)}")
        # If there's an error, run the interface with just the prompt
        run_interface(prompt=prompt)
