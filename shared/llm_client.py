"""
LLM Client - Unified interface for multiple LLM providers
"""

import os
import time
from enum import Enum
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from groq import Groq
from openai import OpenAI

from .schemas import LLMProvider
from .utils import get_logger

logger = get_logger(__name__)


class LLMError(Exception):
    """Base exception for LLM client errors"""

    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM request times out"""

    pass


class LLMRateLimitError(LLMError):
    """Raised when rate limit is exceeded"""

    pass


class LLMClient:
    """
    Unified LLM client that supports multiple providers
    """

    def __init__(
        self,
        provider: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 60,
    ):
        """
        Initialize LLM client

        Args:
            provider: Provider name (groq, openai, anthropic)
            model: Model name (optional, uses defaults if not provided)
            api_key: API key (optional, reads from env if not provided)
            timeout: Request timeout in seconds
        """
        self.provider = provider.lower()
        self.timeout = timeout

        # Set default models if not provided
        if not model:
            model = self._get_default_model(self.provider)

        self.model = model

        # Initialize provider-specific client
        self._client = self._initialize_client(provider, api_key)

        logger.info(f"LLM Client initialized: {provider}/{model}")

    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider"""
        defaults = {
            "groq": "llama-3.3-70b-versatile",
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-5-haiku-20241022",
        }
        return defaults.get(provider.lower(), defaults["groq"])

    def _initialize_client(self, provider: str, api_key: Optional[str]) -> Any:
        """Initialize provider-specific client"""
        provider_lower = provider.lower()

        # Get API key from parameter or environment
        if not api_key:
            api_key = self._get_api_key(provider_lower)

        if not api_key:
            raise ValueError(
                f"API key not found for {provider}. "
                f"Set {self._get_env_key_name(provider_lower)} environment variable."
            )

        try:
            if provider_lower == "groq":
                return Groq(api_key=api_key, timeout=self.timeout)
            elif provider_lower == "openai":
                return OpenAI(api_key=api_key, timeout=self.timeout)
            elif provider_lower == "anthropic":
                return Anthropic(api_key=api_key, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        except Exception as e:
            logger.error(f"Failed to initialize {provider} client: {e}")
            raise

    def _get_api_key(self, provider: str) -> Optional[str]:
        """Get API key from environment"""
        env_key = self._get_env_key_name(provider)
        return os.getenv(env_key)

    def _get_env_key_name(self, provider: str) -> str:
        """Get environment variable name for API key"""
        mapping = {
            "groq": "GROQ_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
        }
        return mapping.get(provider.lower(), f"{provider.upper()}_API_KEY")

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs,
    ) -> str:
        """
        Generate text using the configured LLM with retry logic

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text

        Raises:
            LLMError: If generation fails after all retries
            LLMTimeoutError: If request times out
            LLMRateLimitError: If rate limit is exceeded
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                if self.provider == "groq":
                    return self._generate_groq(
                        messages, temperature, max_tokens, **kwargs
                    )
                elif self.provider == "openai":
                    return self._generate_openai(
                        messages, temperature, max_tokens, **kwargs
                    )
                elif self.provider == "anthropic":
                    return self._generate_anthropic(
                        messages, temperature, max_tokens, **kwargs
                    )
                else:
                    raise ValueError(f"Unsupported provider: {self.provider}")
            except Exception as e:
                last_error = e
                error_str = str(e).lower()

                # Check for rate limit errors
                if any(
                    keyword in error_str
                    for keyword in ["rate limit", "429", "quota", "limit exceeded"]
                ):
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2**attempt)  # Exponential backoff
                        logger.warning(
                            f"Rate limit hit (attempt {attempt + 1}/{max_retries}). "
                            f"Retrying in {wait_time:.1f}s..."
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        raise LLMRateLimitError(
                            f"Rate limit exceeded after {max_retries} attempts: {e}"
                        )

                # Check for timeout errors
                elif any(
                    keyword in error_str
                    for keyword in ["timeout", "timed out", "time out"]
                ):
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Timeout error (attempt {attempt + 1}/{max_retries}). "
                            f"Retrying in {retry_delay:.1f}s..."
                        )
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise LLMTimeoutError(
                            f"Request timed out after {max_retries} attempts: {e}"
                        )

                # Check for transient errors (5xx, connection errors)
                elif any(
                    keyword in error_str
                    for keyword in ["500", "502", "503", "504", "connection", "network"]
                ):
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        logger.warning(
                            f"Transient error (attempt {attempt + 1}/{max_retries}): {e}. "
                            f"Retrying in {wait_time:.1f}s..."
                        )
                        time.sleep(wait_time)
                        continue

                # For other errors, log and re-raise
                logger.error(
                    f"LLM generation failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt == max_retries - 1:
                    raise LLMError(
                        f"LLM generation failed after {max_retries} attempts: {e}"
                    )

        # Should not reach here, but just in case
        raise LLMError(f"LLM generation failed: {last_error}")

    def _generate_groq(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> str:
        """Generate using Groq"""
        try:
            # Convert messages format if needed
            formatted_messages = self._format_messages_for_groq(messages)

            response = self._client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            if not response.choices or not response.choices[0].message.content:
                raise LLMError("Empty response from Groq API")

            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise

    def _generate_openai(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> str:
        """Generate using OpenAI"""
        try:
            formatted_messages = self._format_messages_for_openai(messages)

            response = self._client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            if not response.choices or not response.choices[0].message.content:
                raise LLMError("Empty response from OpenAI API")

            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _generate_anthropic(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> str:
        """Generate using Anthropic"""
        try:
            # Anthropic uses a different message format
            system_message = None
            formatted_messages = []

            # Extract system message if present
            for msg in messages:
                if msg.get("role") == "system":
                    system_message = msg.get("content")
                else:
                    role = msg.get("role", "user")
                    # Anthropic only supports "user" and "assistant" roles
                    if role not in ["user", "assistant"]:
                        role = "user"
                    formatted_messages.append(
                        {"role": role, "content": msg.get("content", "")}
                    )

            # Anthropic requires at least one user message
            if not formatted_messages:
                raise ValueError("Anthropic requires at least one user message")

            response = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message,
                messages=formatted_messages,
                **kwargs,
            )

            if not response.content or not response.content[0].text:
                raise LLMError("Empty response from Anthropic API")

            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    def _format_messages_for_groq(
        self, messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Format messages for Groq API"""
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            # Groq supports system, user, assistant roles
            if role in ["system", "user", "assistant"]:
                formatted.append({"role": role, "content": content})
            else:
                # Convert unknown roles to user
                formatted.append({"role": "user", "content": content})

        return formatted

    def _format_messages_for_openai(
        self, messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Format messages for OpenAI API"""
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            # OpenAI supports system, user, assistant roles
            if role in ["system", "user", "assistant"]:
                formatted.append({"role": role, "content": content})
            else:
                formatted.append({"role": "user", "content": content})

        return formatted


def get_llm_client(
    provider: str,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: int = 60,
) -> LLMClient:
    """
    Factory function to create an LLM client

    Args:
        provider: Provider name (groq, openai, anthropic)
        model: Model name (optional)
        api_key: API key (optional, reads from env if not provided)
        timeout: Request timeout in seconds

    Returns:
        Configured LLMClient instance

    Example:
        >>> client = get_llm_client("groq", model="llama-3.3-70b-versatile")
        >>> response = client.generate([{"role": "user", "content": "Hello"}])
    """
    return LLMClient(provider=provider, model=model, api_key=api_key, timeout=timeout)
