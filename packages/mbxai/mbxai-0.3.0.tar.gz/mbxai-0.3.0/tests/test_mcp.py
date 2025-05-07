"""Tests for the MCP client and server."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Any
from fastapi.testclient import TestClient
import json

from mbxai.mcp import MCPClient, MCPServer
from mbxai.mcp.client import MCPTool
from mbxai.openrouter import OpenRouterClient
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel


# Test models
class TestInput(BaseModel):
    """Test input model."""
    text: str


class TestOutput(BaseModel):
    """Test output model."""
    result: str
    count: int


# Create a FastMCP instance for testing
mcp = FastMCP("test-service")


# Create the test tool
@mcp.tool()
@pytest.mark.skip(reason="This is a tool function, not a test")
async def test_tool(argument: TestInput) -> TestOutput:
    """A test tool that returns a simple response."""
    return TestOutput(
        result=f"Processed: {argument.text}",
        count=len(argument.text)
    )


@pytest.fixture
def openrouter_client():
    """Create a mock OpenRouter client."""
    return Mock(spec=OpenRouterClient)


@pytest.fixture
def mcp_client(openrouter_client):
    """Create an MCP client with a mock OpenRouter client."""
    return MCPClient(openrouter_client)


@pytest.fixture
def mcp_server():
    """Create an MCP server."""
    server = MCPServer("test-service")
    server.app.dependency_overrides = {}  # Clear any overrides
    return server


@pytest.fixture
def test_client(mcp_server):
    """Create a test client for the FastAPI app."""
    return TestClient(mcp_server.app)


@pytest.mark.asyncio
async def test_register_mcp_server(mcp_client):
    """Test registering an MCP server."""
    # Mock the HTTP client
    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "name": "test_tool",
            "description": "A test tool that returns a simple response",
            "input_schema": {
                "$defs": {
                    "TestInput": {
                        "properties": {
                            "text": {
                                "description": "The text to process",
                                "minLength": 1,
                                "title": "Text",
                                "type": "string"
                            }
                        },
                        "required": ["text"],
                        "title": "TestInput",
                        "type": "object"
                    }
                },
                "properties": {
                    "argument": {
                        "$ref": "#/$defs/TestInput"
                    }
                },
                "required": ["argument"],
                "title": "test_toolArguments",
                "type": "object"
            },
            "internal_url": "http://test-server/tools/test_tool/invoke",
            "service": "test-service",
            "strict": True,
            "function": test_tool
        }
    ]
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        
        # Register the server
        async with mcp_client:
            await mcp_client.register_mcp_server(
                name="test-server",
                base_url="http://test-server"
            )
            
            # Verify the server was registered
            assert "test-server" in mcp_client._mcp_servers
            assert mcp_client._mcp_servers["test-server"] == "http://test-server"
            
            # Verify the tool was registered
            assert "test_tool" in mcp_client._tools
            tool = mcp_client._tools["test_tool"]
            assert isinstance(tool, MCPTool)
            assert tool.internal_url == "http://test-server/tools/test_tool/invoke"
            assert tool.service == "test-service"
            assert tool.strict is True


@pytest.mark.asyncio
async def test_add_tool(mcp_server):
    """Test adding a tool to the MCP server."""
    # Add the test tool
    await mcp_server.add_tool(test_tool)
    
    # Verify the tool was added
    assert "test_tool" in mcp_server._tools
    
    # Verify the tool metadata
    tool = mcp_server._tools["test_tool"]
    assert tool.name == "test_tool"
    assert "A test tool that returns a simple response" in tool.description
    assert tool.input_schema["type"] == "object"
    assert tool.strict is True


@pytest.mark.asyncio
async def test_get_tools(test_client, mcp_server):
    """Test getting the list of tools from the MCP server."""
    # Add the test tool
    await mcp_server.add_tool(test_tool)
    
    # Get the tools
    response = test_client.get("/tools")
    assert response.status_code == 200
    
    # Verify the tools
    tools_data = response.json()
    assert len(tools_data) == 1
    assert tools_data[0]["name"] == "test_tool"


@pytest.mark.asyncio
async def test_invoke_tool(test_client, mcp_server):
    """Test invoking a tool through the MCP server."""
    # Add the test tool
    await mcp_server.add_tool(test_tool)
    
    # Invoke the tool
    response = test_client.post(
        "/tools/test_tool/invoke",
        json={"argument": {"text": "test"}}
    )
    assert response.status_code == 200
    
    # Verify the response
    result = response.json()
    assert len(result) == 1
    assert result[0]["type"] == "text"
    output = json.loads(result[0]["text"])
    assert output["result"] == "Processed: test"
    assert output["count"] == 4


@pytest.mark.asyncio
async def test_chat_with_tool(mcp_client):
    """Test using a tool in a chat conversation."""
    # Mock the OpenRouter client
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Here's the result"
    mock_response.choices[0].message.tool_calls = [
        Mock(
            id="call_123",
            function=Mock(
                name="test_tool",
                arguments={"argument": {"text": "test"}}
            )
        )
    ]
    mock_response.choices[0].message.tool_calls[0].function.name = "test_tool"
    
    mcp_client._client.chat_completion.return_value = mock_response
    
    # Mock the HTTP client for tool invocation
    mock_tool_response = Mock()
    mock_tool_response.json.return_value = {
        "result": "Processed: test",
        "count": 4
    }
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_tool_response
        
        # Register a mock server
        mcp_client._mcp_servers["test-server"] = "http://test-server"
        mcp_client._tools["test_tool"] = MCPTool(
            name="test_tool",
            description="A test tool",
            function=test_tool,
            input_schema={
                "$defs": {
                    "TestInput": {
                        "properties": {
                            "text": {
                                "description": "The text to process",
                                "minLength": 1,
                                "title": "Text",
                                "type": "string"
                            }
                        },
                        "required": ["text"],
                        "title": "TestInput",
                        "type": "object"
                    }
                },
                "properties": {
                    "argument": {
                        "$ref": "#/$defs/TestInput"
                    }
                },
                "required": ["argument"],
                "title": "test_toolArguments",
                "type": "object"
            },
            internal_url="http://test-server/tools/test_tool/invoke",
            service="test-service",
            strict=True
        )
        
        # Use the tool in a chat
        async with mcp_client:
            messages = [{"role": "user", "content": "Use the test tool"}]
            response = await mcp_client.chat(messages)
            
            # Verify the response
            assert response.choices[0].message.content == "Here's the result"


@pytest.mark.asyncio
async def test_parse_with_tool(mcp_client):
    """Test using a tool with structured output."""
    # Mock the OpenRouter client
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = '{"result": "Processed: test", "count": 4}'
    mock_response.choices[0].message.tool_calls = [
        Mock(
            id="call_123",
            function=Mock(
                name="test_tool",
                arguments={"argument": {"text": "test"}}
            )
        )
    ]
    mock_response.choices[0].message.tool_calls[0].function.name = "test_tool"
    mock_response.choices[0].message.parsed = TestOutput(result="Processed: test", count=4)
    
    mcp_client._client.chat_completion_parse.return_value = mock_response
    
    # Mock the HTTP client for tool invocation
    mock_tool_response = Mock()
    mock_tool_response.json.return_value = {
        "result": "Processed: test",
        "count": 4
    }
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_tool_response
        
        # Register a mock server
        mcp_client._mcp_servers["test-server"] = "http://test-server"
        mcp_client._tools["test_tool"] = MCPTool(
            name="test_tool",
            description="A test tool",
            function=test_tool,
            input_schema={
                "$defs": {
                    "TestInput": {
                        "properties": {
                            "text": {
                                "description": "The text to process",
                                "minLength": 1,
                                "title": "Text",
                                "type": "string"
                            }
                        },
                        "required": ["text"],
                        "title": "TestInput",
                        "type": "object"
                    }
                },
                "properties": {
                    "argument": {
                        "$ref": "#/$defs/TestInput"
                    }
                },
                "required": ["argument"],
                "title": "test_toolArguments",
                "type": "object"
            },
            internal_url="http://test-server/tools/test_tool/invoke",
            service="test-service",
            strict=True
        )
        
        # Use the tool with structured output
        async with mcp_client:
            messages = [{"role": "user", "content": "Use the test tool"}]
            response = await mcp_client.parse(messages, TestOutput)
            
            # Verify the response
            assert response.choices[0].message.parsed.result == "Processed: test"
            assert response.choices[0].message.parsed.count == 4


@pytest.mark.asyncio
async def test_unknown_tool(test_client):
    """Test handling of unknown tool calls."""
    # Try to invoke an unknown tool
    response = test_client.post(
        "/tools/unknown_tool/invoke",
        json={"input": {"value": "test"}}
    )
    assert response.status_code == 200
    
    # Verify the error response
    result = response.json()
    assert "error" in result
    assert "unknown_tool" in result["error"] 