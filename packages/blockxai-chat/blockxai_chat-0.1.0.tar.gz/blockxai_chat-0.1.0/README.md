# BlockXAI Chat

A Python package that enables developers to create AI chatbots with a single prompt. BlockXAI Chat uses Google's Gemini API to enhance simple prompts into comprehensive system prompts, which are then used with OpenAI's GPT models to generate chatbot responses.

**Includes a preset Gemini API key** - No need to obtain your own Gemini API key to get started!

## Features

- **Simple Prompt Enhancement**: Transform basic prompts into detailed system prompts using Gemini AI
- **Streamlit Interface**: Interactive web interface for chatbot creation and conversation
- **Flexible API**: Use as a package in your code or run as a standalone application
- **Customizable**: Configure model parameters, temperature, and other settings

## Installation

```bash
pip install blockxai-chat
```

## Quick Start

### Method 1: Using the Streamlit Interface

Run the following command to launch the Streamlit interface:

```bash
blockxai-chat
```

Or:

```bash
python -m blockxai_chat.interface
```

### Method 2: Using the Python API

```python
from blockxai_chat.enhancer import enhance_prompt
from blockxai_chat.chatbot import Chatbot
from blockxai_chat.interface import run_interface

# Define a simple prompt
simple_prompt = "A friendly assistant that helps users with their daily tasks."

# Enhance the prompt using Gemini
enhanced_prompt = enhance_prompt(simple_prompt)

# Initialize the chatbot with the enhanced prompt
chatbot = Chatbot(enhanced_prompt)

# Launch the Streamlit interface with the chatbot
run_interface(chatbot)
```

### Method 3: One-Line Creation and Launch

```python
from blockxai_chat.interface import create_and_run

# Create and run the chatbot in one line
create_and_run("A friendly assistant that helps users with their daily tasks.")
```

## Environment Variables

Create a `.env` file in your project directory with the following variable:

```
OPENAI_API_KEY=your_openai_api_key
```

**Note:** A Gemini API key is pre-included in the package, so you don't need to provide one unless you want to use your own key. If you want to use your own key, you can add it to your .env file:

```
GEMINI_API_KEY=your_gemini_api_key
```

Alternatively, you can provide these keys directly in your code or through the Streamlit interface.

## API Reference

### Enhancer Module

```python
from blockxai_chat.enhancer import enhance_prompt

# Enhance a simple prompt
enhanced_prompt = enhance_prompt("A helpful assistant", api_key="your_gemini_api_key")
```

### Chatbot Module

```python
from blockxai_chat.chatbot import Chatbot

# Create a chatbot
chatbot = Chatbot(
    system_prompt="You are a helpful assistant...",
    api_key="your_openai_api_key",
    model="gpt-3.5-turbo"
)

# Get a response
response = chatbot.get_response("Hello, who are you?")

# Clear conversation history
chatbot.clear_history()

# Get conversation history
history = chatbot.get_conversation_history()
```

### Interface Module

```python
from blockxai_chat.interface import run_interface, create_and_run

# Run interface with an existing chatbot
run_interface(chatbot)

# Create and run a chatbot in one line
create_and_run("A helpful assistant")
```

## Development

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests:
   ```bash
   pytest
   ```

## License

MIT License

## Created By

BlockX - Simplifying AI Development
