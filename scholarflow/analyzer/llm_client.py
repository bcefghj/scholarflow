"""Unified LLM client via litellm. Supports OpenAI, Claude, Gemini, DeepSeek, MiniMax, Ollama."""

from __future__ import annotations

from typing import Optional

import litellm

litellm.suppress_debug_info = True


def llm_call(
    prompt: str,
    model: str = "openai/gpt-4o",
    system: str = "You are an expert academic researcher and scientific writer.",
    temperature: float = 0.3,
    max_tokens: int = 8192,
    api_key: Optional[str] = None,
) -> str:
    """Send a prompt to the LLM and return the text response."""
    kwargs: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if api_key:
        kwargs["api_key"] = api_key

    response = litellm.completion(**kwargs)
    return response.choices[0].message.content or ""
