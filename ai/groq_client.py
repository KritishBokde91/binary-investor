"""
Groq API wrapper — llama-3.3-70b-versatile integration with error handling & retries.
"""

from __future__ import annotations

import json
import time
import streamlit as st
from config.settings import settings


class GroqClient:
    """Production-grade Groq API client."""

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.max_tokens = settings.GROQ_MAX_TOKENS
        self.temperature = settings.GROQ_TEMPERATURE
        self._client = None

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)

    def _get_client(self):
        if self._client is None:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except Exception as e:
                st.error(f"Failed to initialize Groq client: {e}")
                return None
        return self._client

    def chat(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None,
        max_retries: int = 3,
    ) -> str:
        """Send a chat completion request with retry logic."""
        if not self.is_available:
            return "⚠️ Groq API key not configured. Please set GROQ_API_KEY in your .env file."

        client = self._get_client()
        if not client:
            return "⚠️ Could not initialize Groq client."

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature or self.temperature,
                    max_tokens=max_tokens or self.max_tokens,
                )
                return response.choices[0].message.content

            except Exception as e:
                error_str = str(e).lower()
                if "rate_limit" in error_str or "429" in error_str:
                    wait = (attempt + 1) * 2
                    time.sleep(wait)
                    continue
                elif attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    return f"⚠️ Groq API error: {e}"

        return "⚠️ Max retries exceeded."

    def chat_with_history(
        self,
        messages: list[dict],
        system_prompt: str = None,
        temperature: float = None,
    ) -> str:
        """Send chat completion with full conversation history."""
        if not self.is_available:
            return "⚠️ Groq API key not configured."

        client = self._get_client()
        if not client:
            return "⚠️ Could not initialize Groq client."

        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"⚠️ Groq API error: {e}"

    def analyze_json(self, prompt: str, system_prompt: str = None) -> dict | None:
        """Send a prompt and parse the response as JSON."""
        response = self.chat(prompt, system_prompt, temperature=0.1)
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        return None
