"""Tests for the tools module."""

import pytest
from unittest.mock import Mock, patch
from pydantic import BaseModel

from mbxai.openrouter import OpenRouterClient
from mbxai.tools import ToolClient, Tool, ToolCall

class TestOutput(BaseModel):
    """Test output model."""
    message: str
    count: int

def test_tool_registration():
    """Test tool registration."""
    # Setup
    openrouter_client = Mock(spec=OpenRouterClient)
    tool_client = ToolClient(openrouter_client)
    
    # Define a test tool
    def test_function(arg1: str) -> str:
        return f"Test: {arg1}"
    
    # Register the tool
    tool_client.register_tool(
        name="test_tool",
        description="A test tool",
        function=test_function,
        schema={
            "type": "object",
            "properties": {
                "arg1": {
                    "type": "string",
                    "description": "Test argument"
                }
            },
            "required": ["arg1"]
        }
    )
    
    # Verify tool was registered
    assert "test_tool" in tool_client._tools
    tool = tool_client._tools["test_tool"]
    assert isinstance(tool, Tool)
    assert tool.name == "test_tool"
    assert tool.description == "A test tool"
    assert tool.function == test_function
    assert tool.schema["type"] == "object"

def test_tool_to_openai_function():
    """Test converting a tool to OpenAI function format."""
    # Create a test tool
    def test_function(arg1: str) -> str:
        return f"Test: {arg1}"
    
    tool = Tool(
        name="test_tool",
        description="A test tool",
        function=test_function,
        schema={
            "type": "object",
            "properties": {
                "arg1": {
                    "type": "string",
                    "description": "Test argument"
                }
            },
            "required": ["arg1"]
        }
    )
    
    # Convert to OpenAI function format
    function_def = tool.to_openai_function()
    
    # Verify the format
    assert function_def["type"] == "function"
    assert "function" in function_def
    assert function_def["function"]["name"] == "test_tool"
    assert function_def["function"]["description"] == "A test tool"
    assert function_def["function"]["parameters"]["type"] == "object"
    assert "arg1" in function_def["function"]["parameters"]["properties"]

def test_chat_without_tools():
    """Test chat without any tools."""
    # Setup
    openrouter_client = Mock(spec=OpenRouterClient)
    tool_client = ToolClient(openrouter_client)
    
    # Mock response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Hello!"
    mock_response.choices[0].message.tool_calls = None
    
    openrouter_client.chat_completion.return_value = mock_response
    
    # Test chat
    messages = [{"role": "user", "content": "Hello"}]
    response = tool_client.chat(messages)
    
    # Verify
    openrouter_client.chat_completion.assert_called_once()
    assert response.choices[0].message.content == "Hello!"

def test_chat_with_tools():
    """Test chat with tool calls."""
    # Setup
    openrouter_client = Mock(spec=OpenRouterClient)
    tool_client = ToolClient(openrouter_client)
    
    # Register a test tool
    def test_function(arg1: str) -> str:
        return f"Result: {arg1}"
    
    tool_client.register_tool(
        name="test_tool",
        description="A test tool",
        function=test_function,
        schema={
            "type": "object",
            "properties": {
                "arg1": {
                    "type": "string",
                    "description": "Test argument"
                }
            },
            "required": ["arg1"]
        }
    )
    
    # Mock responses
    mock_tool_call = Mock()
    mock_tool_call.function = Mock()
    mock_tool_call.function.name = "test_tool"
    mock_tool_call.function.arguments = {"arg1": "test"}
    mock_tool_call.id = "call_123"
    
    mock_response1 = Mock()
    mock_response1.choices = [Mock()]
    mock_response1.choices[0].message = Mock()
    mock_response1.choices[0].message.content = "I'll call the tool"
    mock_response1.choices[0].message.tool_calls = [mock_tool_call]
    
    mock_response2 = Mock()
    mock_response2.choices = [Mock()]
    mock_response2.choices[0].message = Mock()
    mock_response2.choices[0].message.content = "Final response"
    mock_response2.choices[0].message.tool_calls = None
    
    openrouter_client.chat_completion.side_effect = [mock_response1, mock_response2]
    
    # Test chat
    messages = [{"role": "user", "content": "Use the tool"}]
    response = tool_client.chat(messages)
    
    # Verify
    assert openrouter_client.chat_completion.call_count == 2
    assert response.choices[0].message.content == "Final response"

def test_parse_without_tools():
    """Test parse without any tools."""
    # Setup
    openrouter_client = Mock(spec=OpenRouterClient)
    tool_client = ToolClient(openrouter_client)
    
    # Mock response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = '{"message": "Hello", "count": 42}'
    mock_response.choices[0].message.tool_calls = None
    mock_response.choices[0].message.parsed = TestOutput(message="Hello", count=42)
    
    openrouter_client.chat_completion_parse.return_value = mock_response
    
    # Test parse
    messages = [{"role": "user", "content": "Give me structured data"}]
    response = tool_client.parse(messages, TestOutput)
    
    # Verify
    openrouter_client.chat_completion_parse.assert_called_once()
    assert response.choices[0].message.parsed.message == "Hello"
    assert response.choices[0].message.parsed.count == 42

def test_parse_with_tools():
    """Test parse with tool calls."""
    # Setup
    openrouter_client = Mock(spec=OpenRouterClient)
    tool_client = ToolClient(openrouter_client)
    
    # Register a test tool
    def test_function(arg1: str) -> str:
        return f"Result: {arg1}"
    
    tool_client.register_tool(
        name="test_tool",
        description="A test tool",
        function=test_function,
        schema={
            "type": "object",
            "properties": {
                "arg1": {
                    "type": "string",
                    "description": "Test argument"
                }
            },
            "required": ["arg1"]
        }
    )
    
    # Mock responses
    mock_tool_call = Mock()
    mock_tool_call.function = Mock()
    mock_tool_call.function.name = "test_tool"
    mock_tool_call.function.arguments = {"arg1": "test"}
    mock_tool_call.id = "call_123"
    
    mock_response1 = Mock()
    mock_response1.choices = [Mock()]
    mock_response1.choices[0].message = Mock()
    mock_response1.choices[0].message.content = "I'll call the tool"
    mock_response1.choices[0].message.tool_calls = [mock_tool_call]
    
    mock_response2 = Mock()
    mock_response2.choices = [Mock()]
    mock_response2.choices[0].message = Mock()
    mock_response2.choices[0].message.content = '{"message": "Final", "count": 42}'
    mock_response2.choices[0].message.tool_calls = None
    mock_response2.choices[0].message.parsed = TestOutput(message="Final", count=42)
    
    openrouter_client.chat_completion_parse.side_effect = [mock_response1, mock_response2]
    
    # Test parse
    messages = [{"role": "user", "content": "Use the tool and give structured data"}]
    response = tool_client.parse(messages, TestOutput)
    
    # Verify
    assert openrouter_client.chat_completion_parse.call_count == 2
    assert response.choices[0].message.parsed.message == "Final"
    assert response.choices[0].message.parsed.count == 42

def test_streaming_chat():
    """Test streaming chat."""
    # Setup
    openrouter_client = Mock(spec=OpenRouterClient)
    tool_client = ToolClient(openrouter_client)
    
    # Mock response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].delta = Mock()
    mock_response.choices[0].delta.content = "Hello"
    
    # Create a generator for streaming response
    def mock_stream():
        yield mock_response
    
    openrouter_client.chat_completion.return_value = mock_stream()
    
    # Test streaming chat
    messages = [{"role": "user", "content": "Hello"}]
    response = tool_client.chat(messages, stream=True)
    
    # Verify
    openrouter_client.chat_completion.assert_called_once()
    assert next(response).choices[0].delta.content == "Hello"

def test_streaming_parse():
    """Test streaming parse."""
    # Setup
    openrouter_client = Mock(spec=OpenRouterClient)
    tool_client = ToolClient(openrouter_client)
    
    # Mock response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].delta = Mock()
    mock_response.choices[0].delta.content = '{"message": "Hello", "count": 42}'
    
    # Create a generator for streaming response
    def mock_stream():
        yield mock_response
    
    openrouter_client.chat_completion_parse.return_value = mock_stream()
    
    # Test streaming parse
    messages = [{"role": "user", "content": "Give me structured data"}]
    response = tool_client.parse(messages, TestOutput, stream=True)
    
    # Verify
    openrouter_client.chat_completion_parse.assert_called_once()
    assert next(response).choices[0].delta.content == '{"message": "Hello", "count": 42}'

def test_unknown_tool():
    """Test handling of unknown tool calls."""
    # Setup
    openrouter_client = Mock(spec=OpenRouterClient)
    tool_client = ToolClient(openrouter_client)
    
    # Mock response with unknown tool
    mock_tool_call = Mock()
    mock_tool_call.function = Mock()
    mock_tool_call.function.name = "unknown_tool"
    mock_tool_call.function.arguments = {"arg1": "test"}
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "I'll call an unknown tool"
    mock_response.choices[0].message.tool_calls = [mock_tool_call]
    
    openrouter_client.chat_completion.return_value = mock_response
    
    # Test chat with unknown tool
    messages = [{"role": "user", "content": "Use an unknown tool"}]
    with pytest.raises(ValueError, match="Unknown tool: unknown_tool"):
        tool_client.chat(messages) 