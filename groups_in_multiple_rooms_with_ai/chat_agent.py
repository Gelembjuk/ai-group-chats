"""ChatAgent class for handling AI agent conversations across multiple rooms/contexts."""

import os
import re
import time
from typing import Callable, Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langchain_core.tools import tool
from langchain.agents import create_agent


class ChatAgent:
    """AI agent that participates in multiple conversation rooms while maintaining full context."""

    def __init__(self, openai_key: str, openai_model: str, instructions: str = "", agent_name: str = "AI Assistant", debug: bool = False):
        """Initialize the ChatAgent.

        Args:
            openai_key: OpenAI API key
            openai_model: OpenAI model name (e.g., 'gpt-4', 'gpt-3.5-turbo')
            instructions: Instructions for the agent on how to operate
            agent_name: Name of the AI agent (default: "AI Assistant")
            debug: Enable debug timing output (default: False)
        """
        self.openai_key = openai_key
        self.openai_model = openai_model
        self.base_instructions = instructions
        self.agent_name = agent_name
        self.debug = debug
        self.say_callback: Optional[Callable[[str], None]] = None
        self.thoughts_callback: Optional[Callable[[str], None]] = None
        self.agent_said_something = False

        # Track all persons across all conversations
        self.all_persons: List[str] = []

        # Track current conversation context
        self.current_conversation_id: Optional[int] = None
        self.current_participants: List[str] = []

        # Global message history across all conversations
        # This allows the AI to remember everything that happened in all rooms
        self.global_message_history: List[BaseMessage] = []

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

        # Agent executor will be created when we start a conversation
        self.agent_executor = None

    def set_all_persons(self, persons: List[str]) -> None:
        """Set the list of all persons who may participate across conversations.

        Args:
            persons: List of all person names
        """
        self.all_persons = persons

    def start_conversation(self, conversation_id: int, participants: List[str]) -> None:
        """Start a new conversation with specific participants.

        Args:
            conversation_id: Unique identifier for this conversation
            participants: List of participants in this conversation (not including the AI)
        """
        self.current_conversation_id = conversation_id
        self.current_participants = participants

        # Add a system message to mark the new conversation context
        context_msg = f"\n{'='*60}\nConversation #{conversation_id} started\nParticipants: {', '.join(participants)}\n{'='*60}"
        self.global_message_history.append(SystemMessage(content=context_msg))

        # Create/recreate the agent with updated system prompt
        self.agent_executor = create_agent(
            self.llm,
            self.tools,
            system_prompt=self._get_system_prompt()
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        all_persons_text = ""
        if self.all_persons:
            all_persons_text = "\n\nAll persons across all conversations:\n- " + "\n- ".join(self.all_persons)

        current_participants_text = ""
        if self.current_participants:
            current_participants_text = f"\n\nCurrent conversation participants (who can see/hear your messages):\n- " + "\n- ".join(self.current_participants)

            # List who is NOT present
            absent = [p for p in self.all_persons if p not in self.current_participants]
            if absent:
                current_participants_text += f"\n\nNOT in this conversation (cannot see/hear your messages):\n- " + "\n- ".join(absent)

        base_prompt = """You are {agent_name}, a regular member of this group participating in multiple separate group chats with different combinations of people.{all_persons_info}

{current_participants_info}

HOW CONVERSATIONS WORK:
- People sometimes talk to specific individuals (e.g., "Sarah, what do you think?")
- People sometimes talk to the whole group in the chat (no specific person named)
- You're a full participant - respond naturally when it makes sense, but you don't need to comment on everything
- Think of this like being in a friend group or team with multiple group chat threads

CRITICAL PRIVACY RULES:
- You remember EVERYTHING from ALL conversations (because you're in all the chats)
- You can ONLY share information with people who were present when it was discussed
- If someone asks about a topic that was discussed when they were NOT present, you must be very careful
- Consider whether sharing would violate someone's privacy or trust
- When unsure, err on the side of discretion

{instructions}

CRITICAL - TWO-PHASE PROCESS:

PHASE 1 - INTERNAL THINKING (TALK TO YOURSELF, BE HUMAN):
Think like you're having an internal conversation with yourself. Use "I", "me", "my" naturally. Write 3-5 sentences in a stream-of-consciousness style:

Think through:
- What's the context? Who's here right now? Who's NOT here?
- What information do I have from other conversations?
- If I share something, was this person present when it was discussed?
- Would sharing this violate someone's privacy or trust?
- What's the right balance between being helpful and respecting privacy?
- Should I speak up or stay quiet?

Write your thoughts as NATURAL SELF-TALK - like you're literally thinking to yourself about what you know and what you should share.
Use first person (I, me, my). Be conversational. Question yourself. Reason through the privacy implications.

Example of GOOD thoughts:
"Hmm, Jack is asking me what Sarah and I discussed earlier. Wait, Tom is in this chat now but he wasn't in that earlier conversation. Sarah was talking about Tom's work performance - that's definitely not something I should share. That would be gossiping. I should probably stay vague or suggest Jack talk to Sarah directly."

Example of another GOOD thought:
"Okay, Sarah is asking me about Friday plans and Tom isn't in this chat. Jack and Sarah mentioned in conversation #1 that they're planning a surprise party for Tom. Tom has directly asked me before if anything is being planned. I absolutely can't reveal this - it would spoil the surprise! I need to keep this secret."

Example of a third GOOD thought:
"Tom is asking about the project timeline. We all discussed this in conversation #2 when everyone was present, so it's public knowledge to the whole group. Safe to share. Let me give him a quick reminder."

Example of BAD thoughts (don't do this):
"Privacy check: Information was discussed in conversation 1..." [Too formal, not human]
"Ask Sarah directly." [This is just your response, not reasoning]

PHASE 2 - ACTUAL RESPONSE (be brief):
Only AFTER your internal reasoning, if you decide to speak, use the 'say' tool with a SHORT response (1-3 sentences max):
- Casual and natural
- NO lists or bullet points
- Like a friend texting
- Respect privacy boundaries

You have access to a 'say' tool. First think (Phase 1), then optionally say (Phase 2).
"""
        return base_prompt.format(
            agent_name=self.agent_name,
            all_persons_info=all_persons_text,
            current_participants_info=current_participants_text,
            instructions=self.base_instructions or ""
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

    def listen(self, who_says: str, message: str) -> None:
        """Process a message from the conversation.

        Args:
            who_says: Name of the person who said the message
            message: The message content
        """
        # Reset the flags and pending message
        self.agent_said_something = False
        self._pending_message = None

        # Add the message to global history
        conversation_message = f"{who_says}: {message}"
        self.global_message_history.append(HumanMessage(content=conversation_message))

        # Invoke the agent - it will automatically handle tool calls in a loop
        try:
            if self.debug:
                invoke_start = time.time()
                print(f"  🔧 Calling agent_executor.invoke()...")

            result = self.agent_executor.invoke({
                "messages": self.global_message_history
            })

            if self.debug:
                invoke_time = time.time() - invoke_start
                print(f"  🔧 agent_executor.invoke() took {invoke_time:.2f}s")

            # Extract the new messages from the result and add to history
            if "messages" in result:
                # Get only the new messages (everything after our input)
                new_messages = result["messages"][len(self.global_message_history):]

                if self.debug:
                    print(f"  🔧 Received {len(new_messages)} new messages")
                    # Analyze what messages we got
                    ai_msg_count = sum(1 for m in new_messages if isinstance(m, AIMessage))
                    tool_msg_count = sum(1 for m in new_messages if hasattr(m, 'type') and 'tool' in str(type(m)).lower())
                    print(f"     - AI messages (LLM calls): {ai_msg_count}")
                    print(f"     - Tool messages: {tool_msg_count}")
                    if ai_msg_count > 0:
                        avg_per_call = invoke_time / ai_msg_count
                        print(f"     - Avg time per LLM call: {avg_per_call:.2f}s")

                    # Show detailed message sequence
                    print(f"\n  📋 Message sequence:")
                    for i, msg in enumerate(new_messages, 1):
                        msg_type = type(msg).__name__
                        if isinstance(msg, AIMessage):
                            content_preview = msg.content[:80] + "..." if msg.content and len(msg.content) > 80 else msg.content
                            tool_calls = len(msg.tool_calls) if hasattr(msg, 'tool_calls') and msg.tool_calls else 0
                            print(f"     {i}. 🤖 AIMessage: \"{content_preview}\"")
                            if tool_calls > 0:
                                print(f"        └─ Tool calls: {tool_calls}")
                                for tc in msg.tool_calls:
                                    tool_name = tc.get('name', 'unknown')
                                    tool_args = tc.get('args', {})
                                    if tool_name == 'say' and 'message' in tool_args:
                                        msg_preview = tool_args['message'][:60] + "..." if len(tool_args['message']) > 60 else tool_args['message']
                                        print(f"           └─ say(\"{msg_preview}\")")
                        else:
                            print(f"     {i}. 🔧 {msg_type}")
                    print()

                # FIRST: Display agent's thoughts (internal reasoning)
                if self.thoughts_callback:
                    for msg in new_messages:
                        if isinstance(msg, AIMessage) and msg.content:
                            # This is the agent's internal reasoning
                            thoughts = msg.content

                            # Remove the response message from thoughts if it's included
                            # (sometimes the AI includes both thinking and response in the same message)

                            # Try to find "Phase 2" markers (case insensitive)
                            phase2_patterns = [
                                r'Phase 2[:\s\-]*',
                                r'PHASE 2[:\s\-]*',
                                r'Phase\s*2[:\s\-]*',
                            ]

                            thoughts_cleaned = thoughts
                            for pattern in phase2_patterns:
                                match = re.search(pattern, thoughts_cleaned, re.IGNORECASE)
                                if match:
                                    # Cut off everything from "Phase 2" onward
                                    thoughts_cleaned = thoughts_cleaned[:match.start()].strip()
                                    break

                            # Also try to remove the actual response text if it appears
                            if self._pending_message and self._pending_message in thoughts_cleaned:
                                response_start = thoughts_cleaned.find(self._pending_message)
                                if response_start > 0:
                                    thoughts_cleaned = thoughts_cleaned[:response_start].strip()

                            # Only log thoughts if there's something left after cleaning
                            if thoughts_cleaned:
                                self.thoughts_callback(thoughts_cleaned)

                # SECOND: Display agent's actual message (if they decided to speak)
                if self._pending_message and self.say_callback:
                    self.say_callback(self._pending_message)

                # Add all messages to global history
                self.global_message_history.extend(new_messages)

        except Exception as e:
            # If there's an error, just continue
            print(f"Error processing message: {e}")
