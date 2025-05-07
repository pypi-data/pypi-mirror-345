"""
OpenRouter client implementation.
"""

from typing import Any, Optional, Union
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, TypeAdapter
from .models import OpenRouterModel, OpenRouterModelRegistry
from .config import OpenRouterConfig


class OpenRouterError(Exception):
    """Base exception for OpenRouter client errors."""
    pass


class OpenRouterConnectionError(OpenRouterError):
    """Raised when there is a connection error."""
    pass


class OpenRouterAPIError(OpenRouterError):
    """Raised when the API returns an error."""
    pass


class OpenRouterClient:
    """Client for interacting with the OpenRouter API."""

    def __init__(
        self,
        token: str,
        model: Union[str, OpenRouterModel] = OpenRouterModel.GPT4_TURBO,
        base_url: Optional[str] = None,
        default_headers: Optional[dict[str, str]] = None,
    ) -> None:
        """Initialize the OpenRouter client.

        Args:
            token: The OpenRouter API token
            model: The model to use (default: GPT4_TURBO)
            base_url: Optional custom base URL for the API
            default_headers: Optional default headers for API requests

        Raises:
            OpenRouterError: If initialization fails
        """
        try:
            self.config = OpenRouterConfig(
                token=token,
                model=model,
                base_url=base_url or "https://openrouter.ai/api/v1",
                default_headers=default_headers or {
                    "HTTP-Referer": "https://github.com/mibexx/mbxai",
                    "X-Title": "MBX AI",
                }
            )
            
            self._client = OpenAI(
                api_key=token,
                base_url=self.config.base_url,
                default_headers=self.config.default_headers,
            )
        except Exception as e:
            raise OpenRouterError(f"Failed to initialize client: {str(e)}")

    def _handle_api_error(self, operation: str, error: Exception) -> None:
        """Handle API errors.

        Args:
            operation: The operation being performed
            error: The error that occurred

        Raises:
            OpenRouterConnectionError: For connection issues
            OpenRouterAPIError: For API errors
            OpenRouterError: For other errors
        """
        if isinstance(error, OpenAIError):
            raise OpenRouterAPIError(f"API error during {operation}: {str(error)}")
        elif "Connection" in str(error):
            raise OpenRouterConnectionError(f"Connection error during {operation}: {str(error)}")
        else:
            raise OpenRouterError(f"Error during {operation}: {str(error)}")

    @property
    def model(self) -> str:
        """Get the current model."""
        return str(self.config.model)

    @model.setter
    def model(self, value: Union[str, OpenRouterModel]) -> None:
        """Set a new model.

        Args:
            value: The new model to use
        """
        self.config.model = value

    def set_model(self, value: Union[str, OpenRouterModel]) -> None:
        """Set a new model.

        Args:
            value: The new model to use
        """
        self.model = value

    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        *,
        model: Optional[Union[str, OpenRouterModel]] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Create a chat completion.

        Args:
            messages: list of messages
            model: Optional model override
            stream: Whether to stream the response
            **kwargs: Additional parameters

        Returns:
            Completion response

        Raises:
            OpenRouterConnectionError: For connection issues
            OpenRouterAPIError: For API errors
            OpenRouterError: For other errors
        """
        try:
            # Remove any incompatible parameters
            kwargs.pop("parse", None)  # Remove parse parameter if present
            
            return self._client.chat.completions.create(
                model=str(model or self.model),
                messages=messages,
                stream=stream,
                **kwargs,
            )
        except Exception as e:
            self._handle_api_error("chat completion", e)

    def chat_completion_parse(
        self,
        messages: list[dict[str, Any]],
        response_format: type[BaseModel],
        *,
        model: Optional[Union[str, OpenRouterModel]] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Create a chat completion and parse the response.

        Args:
            messages: list of messages
            response_format: Pydantic model to parse the response into
            model: Optional model override
            stream: Whether to stream the response
            **kwargs: Additional parameters

        Returns:
            Parsed completion response

        Raises:
            OpenRouterConnectionError: For connection issues
            OpenRouterAPIError: For API errors
            OpenRouterError: For other errors
            ValueError: If response parsing fails
        """
        try:
            # Add system message to enforce JSON output if not present
            if not any(msg.get("role") == "system" for msg in messages):
                messages.insert(0, {
                    "role": "system",
                    "content": "You are a helpful assistant that responds in valid JSON format."
                })
            
            # Add format instructions to user message
            last_user_msg = next((msg for msg in reversed(messages) if msg.get("role") == "user"), None)
            if last_user_msg:
                format_desc = f"Respond with valid JSON matching this Pydantic model: {response_format.__name__}"
                last_user_msg["content"] = f"{format_desc}\n\n{last_user_msg['content']}"
            
            response = self.chat_completion(
                messages,
                model=model,
                stream=stream,
                response_format={"type": "json_object"},  # Force JSON response
                **kwargs
            )
            
            if stream:
                return response

            # Parse the response content into the specified format
            content = response.choices[0].message.content
            adapter = TypeAdapter(response_format)
            try:
                parsed = adapter.validate_json(content)
                response.choices[0].message.parsed = parsed
                return response
            except Exception as e:
                raise ValueError(f"Failed to parse response as {response_format.__name__}: {str(e)}")
        except ValueError as e:
            raise e
        except Exception as e:
            self._handle_api_error("chat completion parse", e)

    def embeddings(
        self,
        input: Union[str, list[str]],
        *,
        model: Optional[Union[str, OpenRouterModel]] = None,
        **kwargs: Any,
    ) -> Any:
        """Create embeddings.

        Args:
            input: Text to embed
            model: Optional model override
            **kwargs: Additional parameters

        Returns:
            Embeddings response

        Raises:
            OpenRouterConnectionError: For connection issues
            OpenRouterAPIError: For API errors
            OpenRouterError: For other errors
        """
        try:
            # Remove any incompatible parameters
            kwargs.pop("parse", None)  # Remove parse parameter if present
            
            # Use text-embedding-ada-002 for embeddings
            embeddings_model = "openai/text-embedding-ada-002"
            
            return self._client.embeddings.create(
                model=str(model or embeddings_model),
                input=input if isinstance(input, list) else [input],
                encoding_format="float",  # Use float format instead of base64
                **kwargs,
            )
        except Exception as e:
            self._handle_api_error("embeddings", e)

    @classmethod
    def register_model(cls, name: str, value: str) -> None:
        """Register a new model.

        Args:
            name: The name of the model (e.g., "CUSTOM_MODEL")
            value: The model identifier (e.g., "provider/model-name")

        Raises:
            ValueError: If the model name is already registered.
        """
        OpenRouterModelRegistry.register_model(name, value)

    @classmethod
    def list_models(cls) -> dict[str, str]:
        """List all available models.

        Returns:
            A dictionary mapping model names to their identifiers.
        """
        return OpenRouterModelRegistry.list_models() 