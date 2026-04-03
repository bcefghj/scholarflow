"""Unified LLM client via litellm. Supports OpenAI, Claude, Gemini, DeepSeek, MiniMax, Ollama."""

from __future__ import annotations

import os
import re
from typing import Optional

import litellm

litellm.suppress_debug_info = True

MINIMAX_BASE_URL = "https://api.minimaxi.com/v1"


def _strip_thinking(text: str) -> str:
    """Remove <think>...</think> blocks from model output (e.g. MiniMax M2.7, DeepSeek)."""
    cleaned = re.sub(r"<think>.*?</think>\s*", "", text, flags=re.DOTALL)
    return cleaned.strip()


def _is_minimax(model: str) -> bool:
    return "minimax" in model.lower()


def llm_call(
    prompt: str,
    model: str = "openai/gpt-4o",
    system: str = "You are an expert academic researcher and scientific writer.",
    temperature: float = 0.3,
    max_tokens: int = 8192,
    api_key: Optional[str] = None,
) -> str:
    """Send a prompt to the LLM and return the text response."""
    actual_model = model

    if _is_minimax(model):
        actual_model = "openai/MiniMax-M2.7"
        if not api_key:
            api_key = os.getenv("MINIMAX_API_KEY")

    kwargs: dict = {
        "model": actual_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    if api_key:
        kwargs["api_key"] = api_key

    if _is_minimax(model):
        kwargs["api_base"] = MINIMAX_BASE_URL

    response = litellm.completion(**kwargs)
    content = response.choices[0].message.content or ""

    content = _strip_thinking(content)
    return content
