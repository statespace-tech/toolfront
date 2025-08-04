import ast
import functools
import inspect
import json
import logging
import os
from collections.abc import Callable
from typing import Any, get_args, get_origin

import executing
import pandas as pd
from pydantic import TypeAdapter
from pydantic_ai import ModelRetry
from yarl import URL

from toolfront.config import (
    DEFAULT_ANTHROPIC_MODEL,
    DEFAULT_COHERE_MODEL,
    DEFAULT_GOOGLE_MODEL,
    DEFAULT_MISTRAL_MODEL,
    DEFAULT_OPENAI_MODEL,
    MAX_DATA_CHARS,
    MAX_DATA_ROWS,
)

logger = logging.getLogger("toolfront")
logger.setLevel(logging.INFO)


def prepare_tool_for_pydantic_ai(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that automatically serializes function outputs using serialize_response and handles errors.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function that serializes its output
    """

    # Get the original function signature
    sig = inspect.signature(func)

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            if isinstance(result, dict):
                return {k: serialize_response(v) for k, v in result.items()}
            return serialize_response(result)
        except Exception as e:
            logger.error(f"Tool {func.__name__} failed: {e}", exc_info=True)
            raise ModelRetry(f"Tool {func.__name__} failed: {str(e)}") from e

    wrapper.__signature__ = sig

    return wrapper


def serialize_response(response: Any) -> Any:
    """
    Serialize any response to JSON-compatible format with proper truncation.
    Uses pydantic TypeAdapter for robust serialization of any object type.

    Args:
        response: Response to serialize (can be any type)

    Returns:
        Serialized response with optional truncation message
    """

    if isinstance(response, pd.DataFrame):
        # Truncate by rows if needed
        if len(response) > MAX_DATA_ROWS:
            truncated_df = response.head(MAX_DATA_ROWS)
            json_str = truncated_df.to_csv(index=False)
            return {
                "data": json_str,
                "truncation_message": f"Showing {MAX_DATA_ROWS:,} rows of {len(response):,} total rows",
            }

        # Convert to JSON string
        return response.to_csv(index=False)

    # For all other types, use pydantic TypeAdapter
    adapter = TypeAdapter(Any)
    serialized = adapter.dump_python(response, mode="json")

    # Convert to JSON string to check character count
    json_str = json.dumps(serialized)

    # Handle truncation
    if len(json_str) > MAX_DATA_CHARS:
        truncated_str = json_str[: MAX_DATA_CHARS - 3] + "..."
        return {
            "data": truncated_str,
            "truncation_message": f"Showing {len(truncated_str):,} characters of {len(json_str):,} total characters",
        }

    return serialized


def deserialize_response(tool_result: Any) -> str:
    """Format tool result with proper type handling and truncation."""
    # Handle dict/object results - recursively process each key-value pair
    if isinstance(tool_result, dict):
        if not tool_result:
            return "```json\n{}\n```"

        parts = []
        for k, v in tool_result.items():
            formatted_value = deserialize_response(v)
            parts.append(f"**{k}:**\n{formatted_value}")

        return "\n\n".join(parts)

    # Handle string results - try CSV first, then raw string
    elif isinstance(tool_result, str):
        # Try parsing as CSV first
        try:
            from io import StringIO

            df = pd.read_csv(StringIO(tool_result))
            return f"\n{df.head(10).to_markdown()}\n"
        except Exception:
            # Fallback: treat as raw string and truncate if too long
            if len(tool_result) > 10000:
                tool_result = tool_result[:10000] + "...\n(truncated)"
            return f"\n{tool_result}\n"

    # Handle pandas DataFrame
    elif hasattr(tool_result, "to_markdown"):
        try:
            return f"```markdown\n{tool_result.head(10).to_markdown()}\n```"
        except Exception:
            pass

    # Handle lists
    elif isinstance(tool_result, list):
        if len(tool_result) > 10:
            truncated_list = tool_result[:10] + ["..."]
            result = json.dumps(truncated_list, indent=2)
            return f"```json\n{result}\n```\n\n(showing first 10 of {len(tool_result)} items)"
        else:
            result = json.dumps(tool_result, indent=2)
            return f"```json\n{result}\n```"

    # Handle other types
    else:
        tool_result_str = str(tool_result)
        if len(tool_result_str) > 10000:
            tool_result_str = tool_result_str[:10000] + "...\n(truncated)"
        return f"```\n{tool_result_str}\n```"


def sanitize_url(url: str) -> str:
    """Sanitize the url by removing the password."""
    url = URL(url)
    if url.password:
        url = url.with_password("***")
    return str(url)


def type_allows_none(type_hint: Any) -> bool:
    """
    Check if a type hint allows None values.

    Handles:
    - type(None) / NoneType
    - Optional[T] (which is Union[T, None])
    - T | None (Python 3.10+ union syntax)
    - Union[T, None]
    """
    if type_hint is type(None):
        return True

    # Handle Union types (including Optional)
    origin = get_origin(type_hint)
    if origin is not None:
        # For Union types, check if None is in the args
        args = get_args(type_hint)
        return type(None) in args

    return False


def get_default_model() -> str:
    """Get the default model to use."""
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


def get_output_type_hint() -> Any:
    """
    Get the caller's variable type annotation using the executing library.

    Returns:
        The type annotation or None if not found
    """

    def _contains_node(tree: ast.AST | None, target: ast.AST) -> bool:
        """Check if target node is anywhere in the tree."""
        if tree is None or tree is target:
            return tree is target
        return any(_contains_node(child, target) for child in ast.iter_child_nodes(tree))

    try:
        # Get caller's frame (2 levels up: this function -> ask() -> actual caller)
        frame = inspect.currentframe().f_back.f_back
        source = executing.Source.for_frame(frame)
        node = source.executing(frame).node

        if not node:
            return None

        parent = node.parent

        # Walk up the AST to find the assignment containing our call
        if (
            isinstance(parent, ast.AnnAssign)
            and _contains_node(parent.value, node)
            and isinstance(parent.target, ast.Name)
        ):
            # Found annotated assignment: var: Type = value
            try:
                return eval(ast.unparse(parent.annotation), frame.f_globals, frame.f_locals)
            except Exception:
                return ast.unparse(parent.annotation)

        return None

    except Exception as e:
        logger.debug(f"Could not get caller context: {e}")
        return None
