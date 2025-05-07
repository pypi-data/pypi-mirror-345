"""
Tests for the OpenRouter client.
"""

import pytest
from pydantic import ValidationError
from pydantic import BaseModel
import os
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

from mbxai.openrouter import OpenRouterClient, OpenRouterConfig
from mbxai.openrouter.models import OpenRouterModel

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("OPENROUTER_API_KEY", "test-token")

# Test models
class Step(BaseModel):
    """A step in a coding task."""
    file_path: str
    repo_name: str
    type: str
    diff: str
    description: str
    commit_message: str

class CodingOutput(BaseModel):
    """Structured output for coding tasks."""
    steps: list[Step]

class SimpleOutput(BaseModel):
    """Simple structured output for testing."""
    message: str
    count: int

@pytest.fixture
def client():
    """Create a test client with API key from environment."""
    if not API_KEY or API_KEY == "test-token":
        pytest.skip("OPENROUTER_API_KEY not set in environment")
    return OpenRouterClient(token=API_KEY)

def test_openrouter_config_default_url():
    """Test that OpenRouterConfig accepts default URL."""
    config = OpenRouterConfig(token=API_KEY)
    assert str(config.base_url) == "https://openrouter.ai/api/v1"


def test_openrouter_config_custom_url():
    """Test that OpenRouterConfig accepts custom URL."""
    config = OpenRouterConfig(
        token=API_KEY,
        base_url="https://custom.api.example.com",
    )
    assert str(config.base_url) == "https://custom.api.example.com/"


def test_openrouter_config_invalid_token():
    """Test that OpenRouterConfig validates token format."""
    with pytest.raises(ValueError, match="Token cannot be empty"):
        OpenRouterConfig(token="   ")  # Empty or whitespace-only token


def test_openrouter_config_default_model():
    """Test that OpenRouterConfig uses GPT-4 Turbo as default model."""
    config = OpenRouterConfig(token=API_KEY)
    assert config.model == OpenRouterModel.GPT4_TURBO
    assert config.model.value == "openai/gpt-4-turbo-preview"


def test_openrouter_config_custom_model():
    """Test that OpenRouterConfig accepts custom model."""
    config = OpenRouterConfig(
        token=API_KEY,
        model=OpenRouterModel.CLAUDE_3_OPUS,
    )
    assert str(config.model) == OpenRouterModel.CLAUDE_3_OPUS.value


def test_openrouter_client_initialization():
    """Test OpenRouterClient initialization."""
    client = OpenRouterClient(token=API_KEY)
    assert isinstance(client.config, OpenRouterConfig)
    assert client.config.token == API_KEY
    assert str(client.config.base_url) == "https://openrouter.ai/api/v1/"
    assert client.config.model == OpenRouterModel.GPT4_TURBO


def test_openrouter_client_custom_url():
    """Test OpenRouterClient with custom URL."""
    client = OpenRouterClient(
        token=API_KEY,
        base_url="https://custom.api.example.com",
    )
    assert str(client.config.base_url) == "https://custom.api.example.com/"


def test_openrouter_client_custom_model():
    """Test OpenRouterClient with custom model."""
    client = OpenRouterClient(
        token=API_KEY,
        model=OpenRouterModel.CLAUDE_3_OPUS,
    )
    assert client.config.model == OpenRouterModel.CLAUDE_3_OPUS


def test_openrouter_client_custom_model_and_url():
    """Test OpenRouterClient with custom model and URL."""
    client = OpenRouterClient(
        token=API_KEY,
        model=OpenRouterModel.GEMINI_PRO,
        base_url="https://custom.api.example.com",
    )
    assert client.config.model == OpenRouterModel.GEMINI_PRO
    assert str(client.config.base_url) == "https://custom.api.example.com/"


def test_openrouter_client_set_model():
    """Test setting a new model after client initialization."""
    client = OpenRouterClient(token=API_KEY)
    assert client.config.model == OpenRouterModel.GPT4_TURBO
    
    client.set_model(OpenRouterModel.CLAUDE_3_OPUS)
    assert client.config.model == OpenRouterModel.CLAUDE_3_OPUS
    
    client.set_model(OpenRouterModel.GEMINI_PRO)
    assert client.config.model == OpenRouterModel.GEMINI_PRO


def test_register_custom_model():
    """Test registering a custom model."""
    # Register a new model
    OpenRouterClient.register_model("CUSTOM_MODEL", "custom/model-1")
    
    # Verify the model is in the list
    models = OpenRouterClient.list_models()
    assert "CUSTOM_MODEL" in models
    assert models["CUSTOM_MODEL"] == "custom/model-1"


def test_register_duplicate_model():
    """Test that registering a duplicate model raises an error."""
    # Register a model
    OpenRouterClient.register_model("DUPLICATE_MODEL", "custom/model-2")
    
    # Try to register it again
    with pytest.raises(ValueError, match="Model DUPLICATE_MODEL is already registered"):
        OpenRouterClient.register_model("DUPLICATE_MODEL", "custom/model-3")


def test_list_models_includes_builtin_and_custom():
    """Test that list_models includes both built-in and custom models."""
    # Register a custom model
    OpenRouterClient.register_model("TEST_MODEL", "test/model-1")
    
    # Get all models
    models = OpenRouterClient.list_models()
    
    # Check that both built-in and custom models are present
    assert "GPT4_TURBO" in models  # Built-in
    assert "TEST_MODEL" in models  # Custom
    assert models["GPT4_TURBO"] == "openai/gpt-4-turbo-preview"
    assert models["TEST_MODEL"] == "test/model-1"


@pytest.mark.skipif(not API_KEY or API_KEY == "test-token", reason="OPENROUTER_API_KEY not set")
def test_chat_completion():
    """Test chat completion functionality."""
    client = OpenRouterClient(token=API_KEY)
    messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    response = client.chat_completion(messages)
    assert response is not None
    assert hasattr(response, "choices")
    assert len(response.choices) > 0


@pytest.mark.skipif(not API_KEY or API_KEY == "test-token", reason="OPENROUTER_API_KEY not set")
def test_streaming_chat_completion():
    """Test streaming chat completion functionality."""
    client = OpenRouterClient(token=API_KEY)
    messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    response = client.chat_completion(messages, stream=True)
    assert response is not None
    assert hasattr(response, "__iter__")  # Should be an iterator
    chunks = list(response)  # Collect all chunks
    assert len(chunks) > 0


def test_custom_model_chat_completion():
    """Test chat completion with a custom model."""
    # Register a custom model with a valid provider/model format
    model_name = "TEST_MODEL_" + str(hash("test"))  # Generate unique name
    OpenRouterClient.register_model(model_name, "openai/gpt-3.5-turbo")
    client = OpenRouterClient(token=API_KEY, model=model_name)
    messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    response = client.chat_completion(messages)
    assert response is not None
    assert hasattr(response, "choices")
    assert len(response.choices) > 0


def test_custom_default_headers():
    """Test custom default headers."""
    custom_headers = {
        "HTTP-Referer": "https://custom.example.com",
        "X-Title": "Custom App",
        "X-Custom": "test-value"
    }
    client = OpenRouterClient(
        token=API_KEY,
        default_headers=custom_headers
    )
    assert client.config.default_headers == custom_headers


def test_chat_completion_parse_simple(client):
    """Test chat completion with simple structured output."""
    messages = [
        {
            "content": "You are a helpful assistant.",
            "role": "system",
        },
        {
            "content": "Return a simple message with count 42.",
            "role": "user",
        },
    ]
    
    response = client.chat_completion_parse(
        messages=messages,
        response_format=SimpleOutput,
    )
    
    assert response is not None
    assert hasattr(response, "choices")
    assert len(response.choices) > 0
    assert hasattr(response.choices[0].message, "parsed")
    parsed = response.choices[0].message.parsed
    assert isinstance(parsed, SimpleOutput)
    assert parsed.count == 42
    assert isinstance(parsed.message, str)


def test_chat_completion_parse_coding(client):
    """Test chat completion with coding task structured output."""
    messages = [
        {
            "content": "You are an exceptional principal engineer that is amazing at finding and fixing issues in codebases.",
            "role": "system",
        },
        {
            "content": "We need to enhance error handling in the `from_str` method.",
            "role": "assistant",
        },
        {
            "content": """Break down the task of fixing the issue into steps. Each step should have:
- file_path: The path to the file to modify
- repo_name: The name of the repository
- type: The type of change (e.g., 'fix', 'enhancement', 'refactor')
- diff: The actual code changes
- description: A description of what the change does
- commit_message: A concise commit message

Example format:
{
  "steps": [
    {
      "file_path": "src/example.py",
      "repo_name": "my-repo",
      "type": "fix",
      "diff": "def from_str(self, name: str) -> 'PriorityLevel':\n    try:\n        return self[name.upper()]\n    except KeyError:\n        raise ValueError(f'Invalid priority level: {name}')",
      "description": "Add error handling for invalid priority levels",
      "commit_message": "fix: Add error handling to from_str method"
    }
  ]
}""",
            "role": "user",
        },
    ]
    
    response = client.chat_completion_parse(
        messages=messages,
        response_format=CodingOutput,
    )
    
    assert response is not None
    assert hasattr(response, "choices")
    assert len(response.choices) > 0
    assert hasattr(response.choices[0].message, "parsed")
    parsed = response.choices[0].message.parsed
    assert isinstance(parsed, CodingOutput)
    assert len(parsed.steps) > 0
    for step in parsed.steps:
        assert isinstance(step, Step)
        assert step.file_path
        assert step.repo_name
        assert step.type
        assert step.diff
        assert step.description
        assert step.commit_message


def test_chat_completion_parse_with_tool_calls(client):
    """Test chat completion with structured output and tool calls."""
    messages = [
        {
            "content": "You are an exceptional principal engineer that is amazing at finding and fixing issues in codebases.",
            "role": "system",
        },
        {
            "content": None,  # Important: content must be None for tool calls
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "call_wHhKUvGq8xMyB78PYQrqIqTp",
                    "function": {
                        "name": "expand_document",
                        "arguments": '{"input": "some/document.py", "repo_name": "owner/repo"}',
                    },
                    "type": "function",
                },
            ],
        },
        {
            "content": 'class PriorityLevel(IntEnum):\n    LOW = 25\n    MEDIUM = 50\n    HIGH = 75\n\n    def to_str(self) -> str:\n        return self.name.lower()\n\n    @classmethod\n    def from_str(self, name: str) -> "PriorityLevel":\n        return self[name.upper()]\n',
            "role": "tool",
            "tool_call_id": "call_wHhKUvGq8xMyB78PYQrqIqTp",
        },
        {
            "content": "We need to enhance error handling in the `from_str` method.",
            "role": "assistant",
        },
        {
            "content": """Break down the task of fixing the issue into steps. Each step should have:
- file_path: The path to the file to modify
- repo_name: The name of the repository
- type: The type of change (e.g., 'fix', 'enhancement', 'refactor')
- diff: The actual code changes
- description: A description of what the change does
- commit_message: A concise commit message

Example format:
{
  "steps": [
    {
      "file_path": "src/example.py",
      "repo_name": "my-repo",
      "type": "fix",
      "diff": "def from_str(self, name: str) -> 'PriorityLevel':\\n    try:\\n        return self[name.upper()]\\n    except KeyError:\\n        raise ValueError(f'Invalid priority level: {name}')",
      "description": "Add error handling for invalid priority levels",
      "commit_message": "fix: Add error handling to from_str method"
    }
  ]
}""",
            "role": "user",
        },
    ]
    
    response = client.chat_completion_parse(
        messages=messages,
        response_format=CodingOutput,
    )
    
    assert response is not None
    assert hasattr(response, "choices")
    assert len(response.choices) > 0
    assert hasattr(response.choices[0].message, "parsed")
    parsed = response.choices[0].message.parsed
    assert isinstance(parsed, CodingOutput)
    assert len(parsed.steps) > 0
    for step in parsed.steps:
        assert isinstance(step, Step)
        assert step.file_path
        assert step.repo_name
        assert step.type
        assert step.diff
        assert step.description
        assert step.commit_message


def test_chat_completion_parse_invalid_model(client):
    """Test chat completion with invalid response format."""
    messages = [
        {"role": "user", "content": "Hello"}
    ]
    
    with pytest.raises(ValueError):
        client.chat_completion_parse(
            messages=messages,
            response_format=str,  # Invalid response format
        )


@pytest.mark.skipif(not API_KEY or API_KEY == "test-token", reason="OPENROUTER_API_KEY not set")
def test_chat_completion_parse_streaming(client):
    """Test streaming chat completion with structured output."""
    messages = [
        {"role": "user", "content": "Count to 3."}
    ]
    
    response = client.chat_completion_parse(
        messages=messages,
        response_format=SimpleOutput,
        stream=True,
    )
    
    assert response is not None
    for chunk in response:
        assert hasattr(chunk, "choices")
        assert len(chunk.choices) > 0
        if hasattr(chunk.choices[0], "delta") and chunk.choices[0].delta.content:
            # For streaming responses, we get delta updates
            assert isinstance(chunk.choices[0].delta.content, str)


def test_chat_completion_parse_with_custom_model(client):
    """Test chat completion with a custom model."""
    messages = [
        {
            "role": "system",
            "content": """You are a helpful assistant that responds in valid JSON format.
            When asked to respond, provide a JSON object with two fields:
            - message: a string containing your response
            - count: an integer representing the number of words in your message"""
        },
        {
            "role": "user",
            "content": "Hello"
        }
    ]
    
    response = client.chat_completion_parse(
        messages=messages,
        response_format=SimpleOutput,
        model="anthropic/claude-3-opus-20240229",
    )
    
    assert response is not None
    assert hasattr(response, "choices")
    assert len(response.choices) > 0
    assert hasattr(response.choices[0].message, "parsed")
    parsed = response.choices[0].message.parsed
    assert isinstance(parsed, SimpleOutput)
    assert parsed.message
    assert parsed.count > 0


@pytest.mark.skip(reason="OpenRouter does not support embeddings")
@pytest.mark.skipif(not API_KEY or API_KEY == "test-token", reason="OPENROUTER_API_KEY not set")
def test_embeddings():
    """Test embeddings functionality."""
    client = OpenRouterClient(token=API_KEY)
    text = "This is a test sentence."
    response = client.embeddings(text)
    assert response is not None
    assert hasattr(response, "data")
    assert len(response.data) > 0
    assert hasattr(response.data[0], "embedding")
    assert len(response.data[0].embedding) > 0


@pytest.mark.skip(reason="OpenRouter does not support embeddings")
@pytest.mark.skipif(not API_KEY or API_KEY == "test-token", reason="OPENROUTER_API_KEY not set")
def test_embeddings_parse():
    """Test embeddings with parse functionality."""
    client = OpenRouterClient(token=API_KEY)
    text = "This is a test sentence."

    # Test with parse=True (default)
    parsed_response = client.embeddings(text, parse=True)
    assert parsed_response is not None
    assert isinstance(parsed_response, list)
    assert len(parsed_response) > 0
    assert isinstance(parsed_response[0], list)
    assert len(parsed_response[0]) > 0 