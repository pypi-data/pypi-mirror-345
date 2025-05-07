"""
Type definitions for the tools package.
"""

from typing import Any, Callable, TypedDict, NotRequired
from pydantic import BaseModel

class ToolFunction(TypedDict):
    """OpenAI function definition for a tool."""
    name: str
    description: str
    parameters: dict[str, Any]

class ToolCall(BaseModel):
    """A tool call from the model."""
    id: str
    name: str
    arguments: dict[str, Any]

class Tool(BaseModel):
    """A tool that can be used by the model."""
    name: str
    description: str
    function: Callable[..., Any]
    schema: dict[str, Any]

    def to_openai_function(self) -> ToolFunction:
        """Convert the tool to an OpenAI function definition."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.schema,
        } 