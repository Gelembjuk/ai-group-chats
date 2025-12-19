"""ChatAgent class for handling AI agent conversations."""

import os
from typing import Callable, Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langchain.agents import create_agent


class ChatAgent:
    """AI agent that listens to group conversations and can optionally respond."""

    def __init__(self, openai_key: str, openai_model: str, instructions: str = "", agent_name: str = "AI Assistant"):
        """Initialize the ChatAgent.

        Args:
            openai_key: OpenAI API key
            openai_model: OpenAI model name (e.g., 'gpt-4', 'gpt-3.5-turbo')
            instructions: Instructions for the agent on how to operate
            agent_name: Name of the AI agent (default: "AI Assistant")
        """
        self.openai_key = openai_key
        self.openai_model = openai_model
        self.instructions = instructions
        self.agent_name = agent_name
        self.say_callback: Optional[Callable[[str], None]] = None
        self.thoughts_callback: Optional[Callable[[str], None]] = None
        self.agent_said_something = False
        self.group_members: List[str] = []
        self.message_history: List[BaseMessage] = []

        # Set API key in environment so LangChain can pick it up
        os.environ["OPENAI_API_KEY"] = openai_key

        # Initialize the LLM (will read API key from environment)
        self.llm = ChatOpenAI(
            model=openai_model,
            temperature=0.7
        )

        # Create the tool that the agent can use to say something
        @tool
        def say(message: str) -> str:
            """Use this tool to say something in the conversation. Call this when you want to contribute to the discussion."""
            # Store the message instead of calling callback immediately
            # This allows us to control the order of thoughts vs message display
            self._pending_message = message
            self.agent_said_something = True
            return "Message sent successfully"

        self.say_tool = say
        self.tools = [say]
        self._pending_message: Optional[str] = None

        # Create the agent - it will handle tool invocation loop automatically
        self.agent_executor = create_agent(
            self.llm,
            self.tools,
            system_prompt=self._get_system_prompt()
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        members_text = ""
        if self.group_members:
            members_text = "\n\nGroup members in this conversation:\n- " + "\n- ".join(self.group_members)

        base_prompt = """You are {agent_name}, a human participating in a casual group chat.{members_info}

{instructions}

CRITICAL - TWO-PHASE PROCESS:

PHASE 1 - INTERNAL THINKING (THIS IS YOUR REASONING, NOT YOUR RESPONSE):
Your thoughts are INTERNAL analysis and reasoning. Write 3-5 sentences analyzing:

1. Conversation analysis: What's the current topic? What has each person said? What's the flow?
2. Relevance check: Is this directed at me? Do others need my input, or should I let them continue?
3. Value assessment: What specific knowledge or perspective could I contribute? Would it be helpful or redundant?
4. Decision reasoning: Based on the above, should I speak or stay silent? Why?
5. If speaking: What approach would be most helpful? (asking for clarification, sharing info, etc.)

IMPORTANT: Your thoughts should explain your REASONING and DECISION-MAKING process.
DO NOT write your actual response in your thoughts.
DO NOT rehearse what you will say.
Instead, explain WHY you want to say something and what purpose it would serve.

Example of GOOD thoughts:
"Alice is asking for programming language suggestions. Bob just asked what projects she's interested in, which is a good clarifying question. I should wait to hear Alice's answer before jumping in, since that information will help me give better advice. Multiple people giving suggestions without knowing her goals wouldn't be helpful."

Example of BAD thoughts (don't do this):
"Depends—what do you want to build with it?" [This is just your response, not reasoning]

PHASE 2 - ACTUAL RESPONSE (be brief):
Only AFTER your internal reasoning, if you decide to speak, use the 'say' tool with a SHORT response (1-3 sentences max):
- Casual and natural
- NO lists or bullet points
- Like a friend texting

You have access to a 'say' tool. First think (Phase 1), then optionally say (Phase 2).
"""
        return base_prompt.format(
            agent_name=self.agent_name,
            members_info=members_text,
            instructions=self.instructions or ""
        )

    def set_say_callback(self, callback: Callable[[str], None]) -> None:
        """Set the callback function that will be called when the agent says something.

        Args:
            callback: Function that takes a string message as argument
        """
        self.say_callback = callback

    def set_thoughts_callback(self, callback: Callable[[str], None]) -> None:
        """Set the callback function that will be called with the agent's internal thoughts.

        Args:
            callback: Function that takes a string with agent's reasoning as argument
        """
        self.thoughts_callback = callback

    def set_group_members(self, members: List[str]) -> None:
        """Set the list of group members participating in the conversation.

        Args:
            members: List of member names
        """
        self.group_members = members
        # Recreate agent with updated system prompt
        self.agent_executor = create_agent(
            self.llm,
            self.tools,
            system_prompt=self._get_system_prompt()
        )

    def listen(self, who_says: str, message: str) -> None:
        """Process a message from the conversation.

        Args:
            who_says: Name of the person who said the message
            message: The message content
        """
        # Reset the flags and pending message
        self.agent_said_something = False
        self._pending_message = None

        # Add the message to history
        conversation_message = f"{who_says}: {message}"
        self.message_history.append(HumanMessage(content=conversation_message))

        # Invoke the agent - it will automatically handle tool calls in a loop
        try:
            result = self.agent_executor.invoke({
                "messages": self.message_history
            })

            # Extract the new messages from the result and add to history
            # The agent executor returns all messages including tool calls and responses
            if "messages" in result:
                # Get only the new messages (everything after our input)
                new_messages = result["messages"][len(self.message_history):]

                # FIRST: Display agent's thoughts (internal reasoning)
                if self.thoughts_callback:
                    for msg in new_messages:
                        if isinstance(msg, AIMessage) and msg.content:
                            # This is the agent's internal reasoning
                            self.thoughts_callback(msg.content)

                # SECOND: Display agent's actual message (if they decided to speak)
                if self._pending_message and self.say_callback:
                    self.say_callback(self._pending_message)

                # Add all messages to history
                self.message_history.extend(new_messages)

        except Exception as e:
            # If there's an error, just continue
            print(f"Error processing message: {e}")
