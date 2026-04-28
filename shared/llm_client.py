"""
LLM Client for Red Team AI - supports Groq, OpenAI, and Anthropic
"""
import os
from typing import List, Optional

from dotenv import load_dotenv
load_dotenv()


class LLMClient:
    def __init__(self, provider: str, model: Optional[str] = None, api_key: Optional[str] = None):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self._client = self._init_client()

    _DEFAULT_MODELS = {
        "groq": "llama-3.3-70b-versatile",
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-5-haiku-20241022",
    }

    def _init_client(self):
        # Apply default model if none provided
        if not self.model:
            self.model = self._DEFAULT_MODELS.get(self.provider)

        if self.provider == "groq":
            from groq import Groq
            key = self.api_key or os.getenv("GROQ_API_KEY")
            if not key:
                raise ValueError("GROQ_API_KEY not set")
            return Groq(api_key=key)

        elif self.provider == "openai":
            from openai import OpenAI
            key = self.api_key or os.getenv("OPENAI_API_KEY")
            if not key:
                raise ValueError("OPENAI_API_KEY not set")
            return OpenAI(api_key=key)

        elif self.provider == "anthropic":
            import anthropic
            key = self.api_key or os.getenv("ANTHROPIC_API_KEY")
            if not key:
                raise ValueError("ANTHROPIC_API_KEY not set")
            return anthropic.Anthropic(api_key=key)

        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Choose from: groq, openai, anthropic")

    def generate(self, messages: List[dict], temperature: float = 0.7, max_tokens: int = 1024, **kwargs) -> str:
        """
        Generate a response from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text string
        """
        if self.provider in ("groq", "openai"):
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content

        elif self.provider == "anthropic":
            # Anthropic separates system prompt from conversation messages
            system_content = None
            conversation = []
            for msg in messages:
                if msg["role"] == "system":
                    system_content = msg["content"]
                else:
                    conversation.append(msg)

            create_kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": conversation,
            }
            if system_content:
                create_kwargs["system"] = system_content

            response = self._client.messages.create(**create_kwargs)
            return response.content[0].text

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")


def get_llm_client(provider: str, model: Optional[str] = None, api_key: Optional[str] = None) -> LLMClient:
    return LLMClient(provider=provider, model=model, api_key=api_key)
