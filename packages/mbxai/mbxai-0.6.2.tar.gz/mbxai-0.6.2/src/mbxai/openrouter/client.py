"""
OpenRouter client implementation.
"""

from typing import Any, Optional, Union
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, TypeAdapter, Field
from .models import OpenRouterModel, OpenRouterModelRegistry
from .config import OpenRouterConfig
import logging
import time
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)


class OpenRouterError(Exception):
    """Base exception for OpenRouter client errors."""
    pass


class OpenRouterConnectionError(OpenRouterError):
    """Raised when there is a connection error."""
    pass


class OpenRouterAPIError(OpenRouterError):
    """Raised when the API returns an error."""
    pass


def with_retry(max_retries: int = 3, initial_delay: float = 1.0, max_delay: float = 10.0):
    """Decorator to add retry logic to a function.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_error = None
            delay = initial_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except (OpenRouterConnectionError, OpenRouterAPIError) as e:
                    last_error = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.1f}s...")
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, max_delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")
                        raise last_error
                except Exception as e:
                    # Don't retry other types of errors
                    raise e
            
            raise last_error

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_error = None
            delay = initial_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (OpenRouterConnectionError, OpenRouterAPIError) as e:
                    last_error = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.1f}s...")
                        time.sleep(delay)
                        delay = min(delay * 2, max_delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")
                        raise last_error
                except Exception as e:
                    # Don't retry other types of errors
                    raise e
            
            raise last_error

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


class OpenRouterClient:
    """Client for interacting with the OpenRouter API."""

    def __init__(
        self,
        token: str,
        model: Union[str, OpenRouterModel] = OpenRouterModel.GPT4_TURBO,
        base_url: Optional[str] = None,
        default_headers: Optional[dict[str, str]] = None,
        max_retries: int = 3,
        retry_initial_delay: float = 1.0,
        retry_max_delay: float = 10.0,
    ) -> None:
        """Initialize the OpenRouter client.

        Args:
            token: The OpenRouter API token
            model: The model to use (default: GPT4_TURBO)
            base_url: Optional custom base URL for the API
            default_headers: Optional default headers for API requests
            max_retries: Maximum number of retry attempts (default: 3)
            retry_initial_delay: Initial delay between retries in seconds (default: 1.0)
            retry_max_delay: Maximum delay between retries in seconds (default: 10.0)

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
                },
                max_retries=max_retries,
                retry_initial_delay=retry_initial_delay,
                retry_max_delay=retry_max_delay,
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
        error_msg = str(error)
        logger.error(f"API error during {operation}: {error_msg}")
        
        if isinstance(error, OpenAIError):
            raise OpenRouterAPIError(f"API error during {operation}: {error_msg}")
        elif "Connection" in error_msg:
            raise OpenRouterConnectionError(f"Connection error during {operation}: {error_msg}")
        elif "Expecting value" in error_msg and "line" in error_msg:
            # This is a JSON parsing error, likely due to a truncated or malformed response
            logger.error("JSON parsing error detected. This might be due to a large response or network issues.")
            raise OpenRouterAPIError(f"Response parsing error during {operation}. The response might be too large or malformed.")
        else:
            raise OpenRouterError(f"Error during {operation}: {error_msg}")

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

    @with_retry()
    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Get a chat completion from OpenRouter."""
        try:
            # Log the request details
            logger.info(f"Sending chat completion request to OpenRouter with model: {model or self.model}")
            logger.info(f"Message count: {len(messages)}")
            
            # Calculate total message size for logging
            total_size = sum(len(str(msg)) for msg in messages)
            logger.info(f"Total message size: {total_size} bytes")
            
            response = self._client.chat.completions.create(
                messages=messages,
                model=model or self.model,
                stream=stream,
                **kwargs,
            )
            
            # Log response details
            logger.info("Received response from OpenRouter")
            if hasattr(response, 'choices') and response.choices:
                logger.info(f"Response has {len(response.choices)} choices")
                if hasattr(response.choices[0], 'message'):
                    content = response.choices[0].message.content
                    content_length = len(content) if content else 0
                    logger.info(f"First choice has message with content length: {content_length}")
                    if content_length > 1000000:  # Log warning for very large responses
                        logger.warning(f"Response content is very large ({content_length} bytes)")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response headers: {e.response.headers}")
                try:
                    content = e.response.text
                    logger.error(f"Response content length: {len(content)} bytes")
                    logger.error(f"Response content preview: {content[:1000]}...")
                except:
                    logger.error("Could not read response content")
            self._handle_api_error("chat completion", e)

    @with_retry()
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

    @with_retry()
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