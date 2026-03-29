"""
Unified async LLM client supporting multiple providers:
Ollama, Claude (Anthropic), OpenAI, Groq.
"""

import json
import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Multi-provider LLM client for narrative generation."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a professional report writer.",
        max_tokens: int = 2000,
        temperature: float = 0.3,
    ) -> str:
        """Generate text using the configured LLM provider."""
        try:
            if self.provider == "ollama":
                return await self._generate_ollama(
                    prompt, system_prompt, max_tokens, temperature
                )
            elif self.provider == "claude":
                return await self._generate_claude(
                    prompt, system_prompt, max_tokens, temperature
                )
            elif self.provider == "openai":
                return await self._generate_openai(
                    prompt, system_prompt, max_tokens, temperature
                )
            elif self.provider == "groq":
                return await self._generate_groq(
                    prompt, system_prompt, max_tokens, temperature
                )
            elif self.provider == "azure_openai":
                return await self._generate_azure_openai(
                    prompt, system_prompt, max_tokens, temperature
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as e:
            logger.error(f"LLM generation failed ({self.provider}): {e}")
            raise

    async def _generate_ollama(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate text using Ollama."""
        import httpx

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
            )
            response.raise_for_status()
            return response.json()["response"]

    async def _generate_claude(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate text using Anthropic Claude."""
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = await client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    async def _generate_openai(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate text using OpenAI."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    async def _generate_groq(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate text using Groq."""
        from groq import AsyncGroq

        client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    async def _generate_azure_openai(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate text using Azure OpenAI."""
        from openai import AsyncAzureOpenAI

        client = AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
        response = await client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content


# Singleton instance
llm_client = LLMClient()
