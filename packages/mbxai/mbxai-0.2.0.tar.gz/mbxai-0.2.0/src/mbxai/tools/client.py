"""
ToolClient implementation for MBX AI.
"""

from typing import Any, Callable, TypeVar, cast
from pydantic import BaseModel
from ..openrouter import OpenRouterClient
from .types import Tool, ToolCall

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

    def chat(
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
        
        while True:
            # Add tools to the request if we have any
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

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
            messages.append({"role": "assistant", "content": message.content})

            # If there are no tool calls, we're done
            if not message.tool_calls:
                return response

            # Handle each tool call
            for tool_call in message.tool_calls:
                tool = self._tools.get(tool_call.function.name)
                if not tool:
                    raise ValueError(f"Unknown tool: {tool_call.function.name}")

                # Call the tool
                result = tool.function(**tool_call.function.arguments)

                # Add the tool response to the messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": str(result),
                })

    def parse(
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
        
        while True:
            # Add tools to the request if we have any
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

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
            messages.append({"role": "assistant", "content": message.content})

            # If there are no tool calls, we're done
            if not message.tool_calls:
                return response

            # Handle each tool call
            for tool_call in message.tool_calls:
                tool = self._tools.get(tool_call.function.name)
                if not tool:
                    raise ValueError(f"Unknown tool: {tool_call.function.name}")

                # Call the tool
                result = tool.function(**tool_call.function.arguments)

                # Add the tool response to the messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": str(result),
                }) 