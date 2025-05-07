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
        logger.debug(f"Registered tool: {name}")

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
            logger.debug(f"Using tools: {tools}")
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        while True:
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
            logger.debug(f"Added assistant message: {assistant_message}")

            # If there are no tool calls, we're done
            if not message.tool_calls:
                return response

            # Handle all tool calls before getting the next model response
            tool_responses = []
            for tool_call in message.tool_calls:
                logger.debug(f"Processing tool call: {tool_call}")
                logger.debug(f"Tool call ID: {tool_call.id}")
                logger.debug(f"Tool call function: {tool_call.function}")
                logger.debug(f"Tool call arguments: {tool_call.function.arguments}")

                tool = self._tools.get(tool_call.function.name)
                if not tool:
                    raise ValueError(f"Unknown tool: {tool_call.function.name}")

                # Parse arguments if they're a string
                arguments = tool_call.function.arguments
                logger.debug(f"Raw arguments type: {type(arguments)}")
                logger.debug(f"Raw arguments: {arguments}")

                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                        logger.debug(f"Parsed arguments: {arguments}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse tool arguments: {e}")
                        raise ValueError(f"Invalid tool arguments format: {arguments}")

                # Call the tool
                logger.debug(f"Calling tool {tool.name} with arguments: {arguments}")
                if inspect.iscoroutinefunction(tool.function):
                    result = await tool.function(**arguments)
                else:
                    result = tool.function(**arguments)
                logger.debug(f"Tool result: {result}")

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
                logger.debug(f"Created tool response: {tool_response}")

            # Add all tool responses to the messages
            messages.extend(tool_responses)
            logger.debug(f"Added all tool responses to messages: {tool_responses}")

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
            logger.debug(f"Added assistant message: {assistant_message}")

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
            logger.debug(f"Using tools: {tools}")
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        while True:
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
            logger.debug(f"Added assistant message: {assistant_message}")

            # If there are no tool calls, we're done
            if not message.tool_calls:
                return response

            # Handle all tool calls before getting the next model response
            tool_responses = []
            for tool_call in message.tool_calls:
                logger.debug(f"Processing tool call: {tool_call}")
                logger.debug(f"Tool call ID: {tool_call.id}")
                logger.debug(f"Tool call function: {tool_call.function}")
                logger.debug(f"Tool call arguments: {tool_call.function.arguments}")

                tool = self._tools.get(tool_call.function.name)
                if not tool:
                    raise ValueError(f"Unknown tool: {tool_call.function.name}")

                # Parse arguments if they're a string
                arguments = tool_call.function.arguments
                logger.debug(f"Raw arguments type: {type(arguments)}")
                logger.debug(f"Raw arguments: {arguments}")

                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                        logger.debug(f"Parsed arguments: {arguments}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse tool arguments: {e}")
                        raise ValueError(f"Invalid tool arguments format: {arguments}")

                # Call the tool
                logger.debug(f"Calling tool {tool.name} with arguments: {arguments}")
                if inspect.iscoroutinefunction(tool.function):
                    result = await tool.function(**arguments)
                else:
                    result = tool.function(**arguments)
                logger.debug(f"Tool result: {result}")

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
                logger.debug(f"Created tool response: {tool_response}")

            # Add all tool responses to the messages
            messages.extend(tool_responses)
            logger.debug(f"Added all tool responses to messages: {tool_responses}")

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
            logger.debug(f"Added assistant message: {assistant_message}")

            # If there are no more tool calls, we're done
            if not message.tool_calls:
                return response 