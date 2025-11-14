"""
Claude API client for processing chat messages with MCP tools
"""
from typing import List, Dict, Any, Optional, AsyncGenerator
import anthropic
from anthropic import Anthropic, AsyncAnthropic
from anthropic.types import Message, TextBlock, ToolUseBlock

from .config import settings


class ClaudeClient:
    """Client for interacting with Claude API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = settings.anthropic_model

    async def chat(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        mcp_client: Any,
        max_tool_iterations: int = 5
    ) -> str:
        """
        Process a chat message with Claude, handling tool calls

        Args:
            message: User's message
            conversation_history: Previous conversation messages
            tools: Available MCP tools
            mcp_client: MCP client instance for tool execution
            max_tool_iterations: Maximum number of tool call iterations

        Returns:
            Claude's final response text
        """
        # Build messages list
        messages = []

        # Add conversation history
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })

        # System prompt
        system_prompt = """You are a helpful AI assistant with access to WhatsApp data through MCP tools.

You can:
- Search and read WhatsApp messages
- Search contacts
- Send messages to contacts or groups
- List recent chats
- Access message history with context

When users ask about their WhatsApp messages, use the appropriate tools to fetch and display the information.
Be helpful, concise, and accurate in your responses."""

        # Iteratively call Claude and execute tools
        for iteration in range(max_tool_iterations):
            # Call Claude
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
                tools=tools if tools else anthropic.NOT_GIVEN
            )

            # Check if we got a final response
            if response.stop_reason == "end_turn":
                # Extract text response
                text_content = []
                for block in response.content:
                    if isinstance(block, TextBlock):
                        text_content.append(block.text)
                return "\n".join(text_content)

            # Handle tool calls
            if response.stop_reason == "tool_use":
                # Add assistant's response to messages
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Execute tools and collect results
                tool_results = []

                for block in response.content:
                    if isinstance(block, ToolUseBlock):
                        tool_name = block.name
                        tool_input = block.input

                        print(f"Executing tool: {tool_name} with input: {tool_input}")

                        try:
                            # Call the MCP tool
                            result = await mcp_client.call_tool(tool_name, tool_input)

                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": str(result)
                            })
                        except Exception as e:
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Error: {str(e)}",
                                "is_error": True
                            })

                # Add tool results to messages
                messages.append({
                    "role": "user",
                    "content": tool_results
                })

                # Continue to next iteration to get Claude's response with tool results
                continue

            # If we got here with another stop reason, return what we have
            text_content = []
            for block in response.content:
                if isinstance(block, TextBlock):
                    text_content.append(block.text)
            return "\n".join(text_content) if text_content else "No response generated."

        # Max iterations reached
        return "I apologize, but I couldn't complete the request within the allowed tool execution limit."

    async def chat_stream(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        mcp_client: Any
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat responses from Claude

        Args:
            message: User's message
            conversation_history: Previous conversation messages
            tools: Available MCP tools
            mcp_client: MCP client instance

        Yields:
            Text chunks from Claude's response
        """
        # Build messages list
        messages = []

        # Add conversation history
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })

        system_prompt = """You are a helpful AI assistant with access to WhatsApp data through MCP tools.

You can:
- Search and read WhatsApp messages
- Search contacts
- Send messages to contacts or groups
- List recent chats
- Access message history with context

When users ask about their WhatsApp messages, use the appropriate tools to fetch and display the information.
Be helpful, concise, and accurate in your responses."""

        # Stream the response
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
            tools=tools if tools else anthropic.NOT_GIVEN
        ) as stream:
            async for text in stream.text_stream:
                yield text
