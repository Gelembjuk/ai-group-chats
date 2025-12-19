#!/usr/bin/env python3
"""Main CLI application for the group chat AI agent."""

import json
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console

from chat_agent import ChatAgent

# Load environment variables
load_dotenv()

# Initialize rich console
console = Console()

app = typer.Typer(help="AI agent that listens to group conversations and can respond")


def load_conversation_file(file_path: Path) -> dict:
    """Load and validate the conversation JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary with conversation data
    """
    if not file_path.exists():
        typer.echo(f"Error: File not found: {file_path}", err=True)
        raise typer.Exit(1)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        typer.echo(f"Error: Invalid JSON file: {e}", err=True)
        raise typer.Exit(1)

    # Validate required fields
    if "conversation" not in data:
        typer.echo("Error: JSON file must contain 'conversation' field", err=True)
        raise typer.Exit(1)

    if "group_members" not in data:
        typer.echo("Warning: JSON file does not contain 'group_members' field")

    return data


@app.command()
def run(
    conversation_file: Path = typer.Argument(
        ...,
        help="Path to the JSON file containing the conversation",
        exists=True,
        dir_okay=False,
    ),
    openai_api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        envvar="OPENAI_API_KEY",
        help="OpenAI API key (can also be set via OPENAI_API_KEY env var)",
    ),
    openai_model: str = typer.Option(
        "gpt-4o-mini",
        "--model",
        "-m",
        envvar="OPENAI_MODEL",
        help="OpenAI model to use",
    ),
    show_thoughts: bool = typer.Option(
        False,
        "--show-thoughts",
        "-t",
        help="Show the agent's internal thoughts and reasoning",
    ),
):
    """Run the AI agent on a conversation from a JSON file.

    The JSON file should contain:
    - group_members: List of member names
    - instructions: Instructions for the AI agent
    - conversation: Array of message objects with 'member' and 'message' fields
    """
    # Check for API key
    if not openai_api_key:
        typer.echo(
            "Error: OpenAI API key not provided. Set OPENAI_API_KEY environment variable or use --api-key option.",
            err=True,
        )
        raise typer.Exit(1)

    # Load conversation data
    typer.echo(f"Loading conversation from: {conversation_file}")
    data = load_conversation_file(conversation_file)

    # Extract data
    group_members = data.get("group_members", [])
    instructions = data.get("instructions", "")
    conversation = data.get("conversation", [])
    agent_name = data.get("agent_name", "AI Assistant")

    # Define colors for group members (cycle through these colors)
    member_colors = ["red", "green", "yellow", "blue", "magenta", "cyan"]
    agent_color = "bright_cyan"  # Special color for AI agent

    # Create color mapping for each member
    color_map = {}
    for i, member in enumerate(group_members):
        color_map[member] = member_colors[i % len(member_colors)]

    # Display group info
    console.print(f"[bold {agent_color}]AI Agent:[/bold {agent_color}] {agent_name}")
    if group_members:
        console.print(f"Group members: {', '.join(group_members)}")
    console.print(f"Messages to process: {len(conversation)}")
    console.print("-" * 60)

    # Initialize the agent
    agent = ChatAgent(
        openai_key=openai_api_key,
        openai_model=openai_model,
        instructions=instructions,
        agent_name=agent_name,
    )

    # Track if agent said something
    agent_spoke = False

    def say_callback(message: str):
        """Callback function called when the agent says something."""
        nonlocal agent_spoke
        agent_spoke = True
        console.print(f"[bold {agent_color}]{agent_name}:[/bold {agent_color}] {message}")

    agent.set_say_callback(say_callback)

    # Set up thoughts callback if requested
    if show_thoughts:
        def thoughts_callback(thoughts: str):
            """Callback function called with the agent's internal thoughts."""
            console.print(f"[dim italic]💭 {agent_name}'s thoughts: {thoughts}[/dim italic]")

        agent.set_thoughts_callback(thoughts_callback)

    # Set group members if available
    if group_members:
        agent.set_group_members(group_members)

    # Process each message in the conversation
    for msg in conversation:
        if "member" not in msg or "message" not in msg:
            console.print("[yellow]Warning: Skipping invalid message (missing 'member' or 'message' field)[/yellow]")
            continue

        member = msg["member"]
        message = msg["message"]

        # Print the message with color
        member_color = color_map.get(member, "white")
        console.print(f"[bold {member_color}]{member}:[/bold {member_color}] {message}")
        console.print()

        # Reset the flag
        agent_spoke = False

        # Let the agent process the message with a spinner
        with console.status(f"[bold green]{agent_name} is thinking...", spinner="dots"):
            agent.listen(member, message)

        # If agent didn't say anything, print "silent" in gray
        if not agent_spoke:
            console.print(f"[dim]{agent_name}: silent[/dim]")

        console.print()  # Empty line between messages

    console.print("-" * 60)
    console.print("[bold green]Conversation processing completed.[/bold green]")


if __name__ == "__main__":
    app()
