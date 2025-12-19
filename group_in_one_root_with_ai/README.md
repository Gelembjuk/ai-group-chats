# Group Chat AI Agent

An AI agent that listens to group conversations and can optionally respond when it has something valuable to contribute.

## Features

- Processes conversations from JSON files
- AI agent observes all messages and maintains context
- Agent can respond using a "say" tool when appropriate
- Built with LangChain for easy LLM provider replacement
- CLI interface with Typer
- Configuration via environment variables

## Requirements

- Python 3.11+
- `uv` tool for dependency management
- OpenAI API key

## Installation

1. Install dependencies using `uv`:

```bash
uv sync
```

2. Create a `.env` file with your OpenAI API key:

```bash
cp .env.example .env
# Edit .env and add your API key
```

## Usage

### Basic Usage

Run the agent on a conversation file:

```bash
uv run python main.py example_conversation.json
```

### With Custom Options

Specify a different model:

```bash
uv run python main.py example_conversation.json --model gpt-4
```

Provide API key via command line:

```bash
uv run python main.py example_conversation.json --api-key your_api_key_here
```

### Get Help

```bash
uv run python main.py --help
```

## Conversation JSON Format

The JSON file should have the following structure:

```json
{
  "group_members": ["Alice", "Bob", "Charlie"],
  "instructions": "Instructions for the AI agent on how to behave",
  "conversation": [
    {
      "member": "Alice",
      "message": "Hello everyone!"
    },
    {
      "member": "Bob",
      "message": "Hi Alice!"
    }
  ]
}
```

### Fields

- `group_members` (optional): Array of participant names
- `instructions` (optional): Custom instructions for the AI agent
- `conversation` (required): Array of message objects, each with:
  - `member`: Name of the person speaking
  - `message`: The message content

## How It Works

1. The application reads the conversation JSON file
2. Each message is displayed and processed sequentially
3. The AI agent listens to each message and thinks about it
4. The agent's thoughts are kept internal (not displayed)
5. If the agent decides to respond, it uses the "say" tool and the message is displayed
6. If the agent doesn't respond, "AI Agent: silent" is displayed
7. The agent maintains full conversation context throughout

## Architecture

### ChatAgent Class

The `ChatAgent` class is the core component:

- **Initialization**: Takes OpenAI API key, model name, and instructions
- **set_say_callback()**: Registers a callback function for when the agent speaks
- **listen()**: Processes incoming messages from conversation participants
- **LangChain Integration**: Uses LangChain for LLM interactions, making it easy to swap providers

### LLM Provider

Currently uses OpenAI, but the design allows for easy replacement:
- All LLM interaction is through LangChain
- To switch providers, modify the `ChatAgent.__init__()` method to use a different LangChain chat model

## Example Output

```
Loading conversation from: example_conversation.json
Group members: Alice, Bob, Charlie
Messages to process: 7
------------------------------------------------------------
Alice: Hey everyone! I'm thinking about learning a new programming language. Any suggestions?
AI Agent: silent

Bob: That's great! What kind of projects are you interested in?
AI Agent: silent

Alice: I'm interested in web development and maybe some data analysis.
AI Agent: I'd recommend Python! It's excellent for both web development (with frameworks like Django and Flask) and data analysis (with libraries like pandas and NumPy). It's also beginner-friendly with clear syntax.

...
```

## Configuration

Environment variables (can be set in `.env` file):

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: `gpt-4o-mini`)

## License

MIT
