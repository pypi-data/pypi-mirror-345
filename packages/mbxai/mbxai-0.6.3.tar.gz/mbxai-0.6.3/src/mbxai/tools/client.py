"""
ToolClient implementation for MBX AI.
"""

from typing import Any, Callable, TypeVar, cast
import logging
import inspect
import json
from pydantic import BaseModel
from ..openrouter import OpenRouterClient
from .types import Tool, ToolCall
import asyncio

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class ToolClient:
    """Base class for tool clients."""

    def __init__(self, openrouter_client: OpenRouterClient):
        """Initialize the tool client."""
        self._openrouter_client = openrouter_client
        self._tools: dict[str, Tool] = {}

    def register_tool(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool

    async def invoke_tool(self, tool_name: str, **kwargs: Any) -> Any:
        """Invoke a tool by name."""
        tool = self._tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        
        if not tool.function:
            raise ValueError(f"Tool {tool_name} has no function implementation")
            
        return await tool.function(**kwargs)

    async def chat(self, messages: list[dict[str, str]], model: str) -> Any:
        """Process a chat request with tools."""
        # Convert tools to OpenAI function format
        functions = [tool.to_openai_function() for tool in self._tools.values()]
        
        # Make the chat request
        response = await self._openrouter_client.chat(
            messages=messages,
            model=model,
            functions=functions,
        )
        
        # Validate response
        if not response:
            raise ValueError("No response received from OpenRouter")
            
        if not response.choices:
            raise ValueError("Response missing choices")
            
        choice = response.choices[0]
        if not choice:
            raise ValueError("Empty choice in response")
            
        message = choice.message
        if not message:
            raise ValueError("Choice missing message")
            
        # If message has function call, execute it
        if message.function_call:
            tool_name = message.function_call.name
            tool_args = json.loads(message.function_call.arguments)
            
            # Invoke the tool
            tool_response = await self.invoke_tool(tool_name, **tool_args)
            
            # Add tool response to messages
            messages.append({
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": tool_name,
                    "arguments": message.function_call.arguments,
                },
            })
            messages.append({
                "role": "function",
                "name": tool_name,
                "content": json.dumps(tool_response),
            })
            
            # Get final response
            final_response = await self._openrouter_client.chat(
                messages=messages,
                model=model,
            )
            
            if not final_response or not final_response.choices:
                raise ValueError("No response received after tool execution")
                
            return final_response
            
        return response

    def _truncate_content(self, content: str | None, max_length: int = 100) -> str:
        """Truncate content for logging."""
        if not content:
            return "None"
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."

    def _truncate_dict(self, data: dict[str, Any], max_length: int = 50) -> str:
        """Truncate dictionary values for logging."""
        if not data:
            return "{}"
        truncated = {}
        for k, v in data.items():
            if isinstance(v, str):
                truncated[k] = self._truncate_content(v, max_length)
            elif isinstance(v, dict):
                truncated[k] = self._truncate_dict(v, max_length)
            else:
                truncated[k] = str(v)[:max_length] + "..." if len(str(v)) > max_length else v
        return str(truncated)

    def _validate_message_sequence(self, messages: list[dict[str, Any]], validate_responses: bool = True) -> None:
        """Validate the message sequence for tool calls and responses.
        
        Args:
            messages: The message sequence to validate
            validate_responses: Whether to validate that all tool calls have responses
        """
        tool_call_ids = set()
        tool_response_ids = set()
        
        for i, msg in enumerate(messages):
            role = msg.get("role")
            if role == "assistant" and "tool_calls" in msg:
                # Track tool calls
                for tc in msg["tool_calls"]:
                    tool_call_ids.add(tc["id"])
                    logger.info(f"Found tool call {tc['id']} for {tc['function']['name']} in message {i}")
            elif role == "tool":
                # Track tool responses
                tool_response_ids.add(msg["tool_call_id"])
                logger.info(f"Found tool response for call ID {msg['tool_call_id']} in message {i}")
        
        # Only validate responses if requested
        if validate_responses:
            # Check for missing responses
            missing_responses = tool_call_ids - tool_response_ids
            if missing_responses:
                logger.error(f"Missing tool responses for call IDs: {missing_responses}")
                logger.error("Message sequence:")
                for i, msg in enumerate(messages):
                    role = msg.get("role", "unknown")
                    if role == "assistant" and "tool_calls" in msg:
                        logger.error(f"  Message {i} - Assistant with tool calls: {[tc['id'] for tc in msg['tool_calls']]}")
                    elif role == "tool":
                        logger.error(f"  Message {i} - Tool response for call ID: {msg['tool_call_id']}")
                    else:
                        logger.error(f"  Message {i} - {role}: {self._truncate_content(msg.get('content'))}")
                raise ValueError(f"Invalid message sequence: missing responses for tool calls {missing_responses}")

    def _log_messages(self, messages: list[dict[str, Any]], validate_responses: bool = True) -> None:
        """Log the messages being sent to OpenRouter.
        
        Args:
            messages: The messages to log
            validate_responses: Whether to validate that all tool calls have responses
        """
        logger.info("Sending messages to OpenRouter:")
        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = self._truncate_content(msg.get("content"))
            tool_calls = msg.get("tool_calls", [])
            tool_call_id = msg.get("tool_call_id")
            
            if tool_calls:
                tool_call_info = [
                    f"{tc['function']['name']}(id={tc['id']})"
                    for tc in tool_calls
                ]
                logger.info(f"  Message {i} - {role}: content='{content}', tool_calls={tool_call_info}")
            elif tool_call_id:
                logger.info(f"  Message {i} - {role}: content='{content}', tool_call_id={tool_call_id}")
            else:
                logger.info(f"  Message {i} - {role}: content='{content}'")
        
        # Validate message sequence
        self._validate_message_sequence(messages, validate_responses)

    async def _process_tool_calls(self, message: Any, messages: list[dict[str, Any]]) -> None:
        """Process all tool calls in a message.
        
        Args:
            message: The message containing tool calls
            messages: The list of messages to add responses to
        """
        if not message.tool_calls:
            return

        # Process all tool calls first
        tool_responses = []
        for tool_call in message.tool_calls:
            tool = self._tools.get(tool_call.function.name)
            if not tool:
                raise ValueError(f"Unknown tool: {tool_call.function.name}")

            # Parse arguments if they're a string
            arguments = tool_call.function.arguments
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse tool arguments: {e}")
                    raise ValueError(f"Invalid tool arguments format: {arguments}")

            # Call the tool
            logger.info(f"Calling tool: {tool.name} with args: {self._truncate_dict(arguments)}")
            if inspect.iscoroutinefunction(tool.function):
                result = await tool.function(**arguments)
            else:
                result = tool.function(**arguments)

            # Convert result to JSON string if it's not already
            if not isinstance(result, str):
                result = json.dumps(result)

            # Create the tool response
            tool_response = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
            tool_responses.append(tool_response)
            logger.info(f"Created tool response for call ID {tool_call.id}")

        # Add all tool responses to the messages
        messages.extend(tool_responses)
        logger.info(f"Message count: {len(messages)}, Added {len(tool_responses)} tool responses to messages")

        # Validate the message sequence
        self._validate_message_sequence(messages, validate_responses=True)

        # Log the messages we're about to send
        self._log_messages(messages, validate_responses=False)

    async def parse(
        self,
        messages: list[dict[str, Any]],
        response_format: type[T],
        *,
        model: str | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Chat with the model and parse the response into a Pydantic model.

        Args:
            messages: The conversation messages
            response_format: The Pydantic model to parse the response into
            model: Optional model override
            stream: Whether to stream the response
            **kwargs: Additional parameters for the chat completion

        Returns:
            The parsed response from the model
        """
        tools = [tool.to_openai_function() for tool in self._tools.values()]
        
        if tools:
            logger.info(f"Available tools: {[tool['function']['name'] for tool in tools]}")
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        while True:
            # Log messages before sending to OpenRouter
            self._log_messages(messages)
            
            # Get the model's response
            response = await self._openrouter_client.chat_completion_parse(
                messages=messages,
                response_format=response_format,
                model=model,
                stream=stream,
                **kwargs,
            )

            if stream:
                return response

            if not response or not response.choices:
                raise ValueError("No response received from OpenRouter")
                
            choice = response.choices[0]
            if not choice:
                raise ValueError("Empty choice in response")
                
            message = choice.message
            if not message:
                raise ValueError("Choice missing message")

            # Check for tool calls first
            if message.tool_calls:
                # Add the assistant's message with tool calls
                assistant_message = {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                        for tool_call in message.tool_calls
                    ]
                }
                messages.append(assistant_message)
                logger.info(f"Message count: {len(messages)}, Added assistant message with tool calls: {[tc.function.name for tc in message.tool_calls]}")

                # Process all tool calls
                await self._process_tool_calls(message, messages)

                # Continue the loop to get the next response
                continue

            # If we have a parsed response, return it
            if hasattr(message, "parsed") and message.parsed:
                return response

            # If we have content but no tool calls, try to parse it
            if message.content:
                try:
                    return response
                except Exception as e:
                    logger.error(f"Failed to parse response: {e}")
                    raise ValueError(f"Failed to parse response as {response_format.__name__}: {str(e)}")

            # If we have neither parsed content nor tool calls, something is wrong
            raise ValueError("Response has neither parsed content nor tool calls") 