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

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class ToolClient:
    """Client for handling tool calls with OpenRouter."""

    def __init__(self, openrouter_client: OpenRouterClient) -> None:
        """Initialize the ToolClient.

        Args:
            openrouter_client: The OpenRouter client to use
        """
        self._client = openrouter_client
        self._tools: dict[str, Tool] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        function: Callable[..., Any],
        schema: dict[str, Any],
    ) -> None:
        """Register a new tool.

        Args:
            name: The name of the tool
            description: A description of what the tool does
            function: The function to call when the tool is used
            schema: The JSON schema for the tool's parameters
        """
        tool = Tool(
            name=name,
            description=description,
            function=function,
            schema=schema,
        )
        self._tools[name] = tool
        logger.info(f"Registered tool: {name}")

    def _truncate_content(self, content: str | None, max_length: int = 100) -> str:
        """Truncate content for logging."""
        if not content:
            return "None"
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."

    def _log_messages(self, messages: list[dict[str, Any]]) -> None:
        """Log the messages being sent to OpenRouter."""
        logger.info("Sending messages to OpenRouter:")
        for msg in messages:
            role = msg.get("role", "unknown")
            content = self._truncate_content(msg.get("content"))
            tool_calls = msg.get("tool_calls", [])
            tool_call_id = msg.get("tool_call_id")
            
            if tool_calls:
                tool_call_info = [
                    f"{tc['function']['name']}(id={tc['id']})"
                    for tc in tool_calls
                ]
                logger.info(f"  {role}: content='{content}', tool_calls={tool_call_info}")
            elif tool_call_id:
                logger.info(f"  {role}: content='{content}', tool_call_id={tool_call_id}")
            else:
                logger.info(f"  {role}: content='{content}'")

        # Validate tool call responses
        tool_call_ids = set()
        tool_response_ids = set()
        
        for msg in messages:
            if msg.get("role") == "assistant" and "tool_calls" in msg:
                for tc in msg["tool_calls"]:
                    tool_call_ids.add(tc["id"])
            elif msg.get("role") == "tool":
                tool_response_ids.add(msg["tool_call_id"])
        
        missing_responses = tool_call_ids - tool_response_ids
        if missing_responses:
            logger.error(f"Missing tool responses for call IDs: {missing_responses}")
            logger.error("Message sequence:")
            for msg in messages:
                role = msg.get("role", "unknown")
                if role == "assistant" and "tool_calls" in msg:
                    logger.error(f"  Assistant message with tool calls: {[tc['id'] for tc in msg['tool_calls']]}")
                elif role == "tool":
                    logger.error(f"  Tool response for call ID: {msg['tool_call_id']}")

    async def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Chat with the model, handling tool calls.

        Args:
            messages: The conversation messages
            model: Optional model override
            stream: Whether to stream the response
            **kwargs: Additional parameters for the chat completion

        Returns:
            The final response from the model
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
            response = self._client.chat_completion(
                messages=messages,
                model=model,
                stream=stream,
                **kwargs,
            )

            if stream:
                return response

            message = response.choices[0].message
            # Add the assistant's message with tool calls
            assistant_message = {
                "role": "assistant",
                "content": message.content or None,  # Ensure content is None if empty
            }
            if message.tool_calls:
                assistant_message["tool_calls"] = [
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
            messages.append(assistant_message)
            logger.info(f"Assistant message: content='{self._truncate_content(message.content)}', tool_calls={[tc.function.name for tc in message.tool_calls] if message.tool_calls else None}")

            # If there are no tool calls, we're done
            if not message.tool_calls:
                return response

            # Handle all tool calls before getting the next model response
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
                logger.info(f"Calling tool: {tool.name} with args: {self._truncate_content(json.dumps(arguments))}")
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
                logger.info(f"Tool response for call ID {tool_call.id}: {self._truncate_content(result)}")

            # Add all tool responses to the messages
            messages.extend(tool_responses)

            # Get a new response from the model with all tool results
            response = self._client.chat_completion(
                messages=messages,
                model=model,
                stream=stream,
                **kwargs,
            )

            if stream:
                return response

            message = response.choices[0].message
            # Add the assistant's message with tool calls
            assistant_message = {
                "role": "assistant",
                "content": message.content or None,  # Ensure content is None if empty
            }
            if message.tool_calls:
                assistant_message["tool_calls"] = [
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
            messages.append(assistant_message)
            logger.info(f"Assistant message: content='{self._truncate_content(message.content)}', tool_calls={[tc.function.name for tc in message.tool_calls] if message.tool_calls else None}")

            # If there are no more tool calls, we're done
            if not message.tool_calls:
                return response

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
            response = self._client.chat_completion_parse(
                messages=messages,
                response_format=response_format,
                model=model,
                stream=stream,
                **kwargs,
            )

            if stream:
                return response

            message = response.choices[0].message
            # Add the assistant's message with tool calls
            assistant_message = {
                "role": "assistant",
                "content": message.content or None,  # Ensure content is None if empty
            }
            if message.tool_calls:
                assistant_message["tool_calls"] = [
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
            messages.append(assistant_message)
            logger.info(f"Assistant message: content='{self._truncate_content(message.content)}', tool_calls={[tc.function.name for tc in message.tool_calls] if message.tool_calls else None}")

            # If there are no tool calls, we're done
            if not message.tool_calls:
                return response

            # Handle all tool calls before getting the next model response
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
                logger.info(f"Calling tool: {tool.name} with args: {self._truncate_content(json.dumps(arguments))}")
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
                logger.info(f"Tool response: {self._truncate_content(result)}")

            # Add all tool responses to the messages
            messages.extend(tool_responses)

            # Get a new response from the model with all tool results
            response = self._client.chat_completion_parse(
                messages=messages,
                response_format=response_format,
                model=model,
                stream=stream,
                **kwargs,
            )

            if stream:
                return response

            message = response.choices[0].message
            # Add the assistant's message with tool calls
            assistant_message = {
                "role": "assistant",
                "content": message.content or None,  # Ensure content is None if empty
            }
            if message.tool_calls:
                assistant_message["tool_calls"] = [
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
            messages.append(assistant_message)
            logger.info(f"Assistant message: content='{self._truncate_content(message.content)}', tool_calls={[tc.function.name for tc in message.tool_calls] if message.tool_calls else None}")

            # If there are no more tool calls, we're done
            if not message.tool_calls:
                return response 