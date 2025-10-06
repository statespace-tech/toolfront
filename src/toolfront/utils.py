import os
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

from pydantic_ai.messages import ModelMessage, ToolReturnPart

DEFAULT_OPENAI_MODEL = "openai:gpt-5"
DEFAULT_ANTHROPIC_MODEL = "anthropic:claude-sonnet-4-0"
DEFAULT_GOOGLE_MODEL = "google-vertex:gemini-2.5-pro"
DEFAULT_MISTRAL_MODEL = "mistral:mistral-large-latest"
DEFAULT_COHERE_MODEL = "cohere:command-r"


def get_model_from_env() -> str:
    """Get the default model to use based on environment variables."""
    if model := os.getenv("TOOLFRONT_MODEL"):
        return model

    if os.getenv("OPENAI_API_KEY"):
        return DEFAULT_OPENAI_MODEL
    elif os.getenv("ANTHROPIC_API_KEY"):
        return DEFAULT_ANTHROPIC_MODEL
    elif os.getenv("GOOGLE_API_KEY"):
        return DEFAULT_GOOGLE_MODEL
    elif os.getenv("MISTRAL_API_KEY"):
        return DEFAULT_MISTRAL_MODEL
    elif os.getenv("COHERE_API_KEY"):
        return DEFAULT_COHERE_MODEL
    raise ValueError("Please specify an API key and model to use")


def clean_url(url: str) -> str:
    """Get the full URL for a given URL."""

    parsed = urlparse(url)

    if parsed.scheme == "" and parsed.netloc == "":
        parsed = urlparse(Path(url).resolve().as_uri())

    parsed = parsed._replace(path=parsed.path.rstrip("/"))

    return urlunparse(parsed)


async def message_at_index_contains_tool_return_parts(messages: list[ModelMessage], index: int) -> bool:
    return any(isinstance(part, ToolReturnPart) for part in messages[index].parts)


def history_processor(context_window: int | None = None) -> Callable[[list[ModelMessage]], Any] | None:
    """Create a history processor that keeps recent messages within context window."""
    if not context_window:
        return None

    async def keep_recent_messages(messages: list[ModelMessage]) -> list[ModelMessage]:
        number_of_messages = len(messages)
        if number_of_messages <= context_window:
            return messages
        if await message_at_index_contains_tool_return_parts(messages, number_of_messages - context_window):
            return messages
        return [messages[0]] + messages[-context_window:]

    return keep_recent_messages
