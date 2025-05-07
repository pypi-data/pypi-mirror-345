"""MCP client implementation."""

from typing import Any, TypeVar, Callable
import httpx
from pydantic import BaseModel, Field

from ..tools import ToolClient, Tool
from ..openrouter import OpenRouterClient


T = TypeVar("T", bound=BaseModel)


class MCPTool(Tool):
    """MCP tool definition."""
    internal_url: str | None = Field(default=None, description="The internal URL to invoke the tool")
    service: str = Field(description="The service that provides the tool")
    strict: bool = Field(default=True, description="Whether the tool response is strictly validated")
    input_schema: dict[str, Any] = Field(description="The input schema for the tool")

    def to_openai_function(self) -> dict[str, Any]:
        """Convert the tool to an OpenAI function definition."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._convert_to_openai_schema(self.input_schema)
        }

    def _convert_to_openai_schema(self, mcp_schema: dict[str, Any]) -> dict[str, Any]:
        """Convert MCP schema to OpenAI schema format."""
        if not mcp_schema:
            return {"type": "object", "properties": {}}

        # If schema has a $ref, resolve it
        if "$ref" in mcp_schema:
            ref = mcp_schema["$ref"].split("/")[-1]
            mcp_schema = mcp_schema.get("$defs", {}).get(ref, {})

        # If schema has an input wrapper, unwrap it
        if "properties" in mcp_schema and "input" in mcp_schema["properties"]:
            input_schema = mcp_schema["properties"]["input"]
            if "$ref" in input_schema:
                ref = input_schema["$ref"].split("/")[-1]
                input_schema = mcp_schema.get("$defs", {}).get(ref, {})
            return input_schema

        return mcp_schema


class MCPClient(ToolClient):
    """MCP client that extends ToolClient to support MCP tool servers."""

    def __init__(self, openrouter_client: OpenRouterClient):
        """Initialize the MCP client."""
        super().__init__(openrouter_client)
        self._mcp_servers: dict[str, str] = {}
        self._http_client = httpx.AsyncClient()

    async def __aenter__(self):
        """Enter the async context."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context."""
        await self._http_client.aclose()

    def _create_tool_function(self, tool: MCPTool) -> Callable[..., Any]:
        """Create a function that invokes an MCP tool."""
        async def tool_function(**kwargs: Any) -> Any:
            # If kwargs has input wrapper, unwrap it
            if "input" in kwargs:
                kwargs = kwargs["input"]

            # Get the URL to use for the tool
            url = tool.internal_url
            if url is None:
                # Use the MCP server URL as fallback
                server_url = self._mcp_servers.get(tool.service)
                if server_url is None:
                    raise ValueError(f"No MCP server found for service {tool.service}")
                url = f"{server_url}/tools/{tool.name}/invoke"

            # Make the HTTP request to the tool's URL
            response = await self._http_client.post(
                url,
                json={"input": kwargs} if tool.strict else kwargs
            )
            return response.json()
        
        # Create a sync wrapper for the async function
        def sync_tool_function(**kwargs: Any) -> Any:
            import asyncio
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(tool_function(**kwargs))
        
        return sync_tool_function

    async def register_mcp_server(self, name: str, base_url: str) -> None:
        """Register an MCP server and load its tools."""
        self._mcp_servers[name] = base_url.rstrip("/")
        
        # Fetch tools from the server
        response = await self._http_client.get(f"{base_url}/tools")
        tools_data = response.json()
        
        # Register each tool
        for tool_data in tools_data:
            # Create MCPTool instance
            tool = MCPTool(**tool_data)
            
            # Create the tool function
            tool_function = self._create_tool_function(tool)
            
            # Register the tool with ToolClient
            self._tools[tool.name] = tool
            tool.function = tool_function 