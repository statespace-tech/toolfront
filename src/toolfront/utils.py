import ast
import inspect
import logging
import os
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlparse

import executing
import yaml
from fsspec import filesystem
from pydantic_ai.messages import ModelMessage, ToolReturnPart

DEFAULT_OPENAI_MODEL = "openai:gpt-4o"
DEFAULT_ANTHROPIC_MODEL = "anthropic:claude-3-5-sonnet-latest"
DEFAULT_GOOGLE_MODEL = "google-vertex:gemini-2.5-pro"
DEFAULT_MISTRAL_MODEL = "mistral:mistral-large-latest"
DEFAULT_COHERE_MODEL = "cohere:command-r"


logger = logging.getLogger("toolfront")
logger.setLevel(logging.INFO)

JSDOC_TO_PYTHON = {
    "string": str,
    "number": float,
    "boolean": bool,
    "any": Any,
    "Object": dict,
    "Array": list,
    "undefined": type(None),
    "null": type(None),
}


@contextmanager
def change_dir(destination):
    prev_dir = Path.cwd()  # save current directory
    os.chdir(destination)  # change to new directory
    try:
        yield
    finally:
        os.chdir(prev_dir)  # restore original directory


def get_model_from_env() -> str:
    if model := os.getenv("TOOLFRONT_MODEL"):
        return model

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


def clean_url(url: str) -> str:
    """Get the full URL for a given URL."""

    parsed = urlparse(url)

    if parsed.scheme == "" and parsed.netloc == "":
        url = Path(url).resolve().as_uri()

    return url


def get_filesystem(url: str, params: dict[str, str] | list[str] | None = None) -> tuple:
    parsed = urlparse(url)

    kwargs = dict(parse_qsl(parsed.query, keep_blank_values=True))

    if isinstance(params, (list | tuple)):
        params = dict([param.split("=") for param in params])

    kwargs.update(params or {})

    fs = filesystem(parsed.scheme, **kwargs)

    if not fs.exists(parsed.path):
        raise FileNotFoundError(f"Not found: {url}")

    return fs


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


def parse_markdown_with_frontmatter(markdown: str) -> tuple[str, dict[str, Any]]:
    """Parse frontmatter from markdown content and return both raw markdown and commands in frontmatter.

    Args:
        markdown: Raw markdown content with optional frontmatter

    Returns:
        Tuple of (raw_markdown_without_frontmatter, frontmatter_commands)
    """
    frontmatter_pattern = r"^\n*---\s*\n(.*?)\n---\s*\n(.*)"
    match = re.match(frontmatter_pattern, markdown, re.DOTALL)

    if not match:
        return markdown, []
    try:
        return match.group(2), yaml.safe_load(match.group(1))
    except Exception as e:
        logger.warning(f"Failed to parse frontmatter YAML: {e}")
        return markdown, []


async def message_at_index_contains_tool_return_parts(messages: list[ModelMessage], index: int) -> bool:
    return any(isinstance(part, ToolReturnPart) for part in messages[index].parts)


def history_processor(context_window: int | None = None) -> callable:
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
