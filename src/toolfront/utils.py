"""
Data serialization utilities for converting DataFrames and other data structures.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from urllib.parse import urlparse, urlunparse

import pandas as pd
from jellyfish import jaro_winkler_similarity
from pydantic import TypeAdapter
from rank_bm25 import BM25Okapi

from toolfront.config import MAX_DATA_CHARS, MAX_DATA_ROWS


def mask_database_password(url: str) -> str:
    """
    Mask only the password portion of a database URL.

    Examples:
        postgresql://user:password@host:5432/db -> postgresql://user:***@host:5432/db
        sqlite:///path/to/db.sqlite -> sqlite:///path/to/db.sqlite (unchanged)
    """
    parsed = urlparse(url)

    # Only mask if there's a password field (even if empty)
    if parsed.password is not None:
        # Replace password with asterisks, keeping username if present
        netloc = f"{parsed.username}:***@{parsed.hostname}" if parsed.username else f"***@{parsed.hostname}"

        # Add port if present
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"

        # Reconstruct URL with masked password
        return urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))

    # Return unchanged if no password
    return url


class HTTPMethod(str, Enum):
    """Valid HTTP methods."""

    GET = "GET"
    # TODO: Implement write methods


class SearchMode(str, Enum):
    """Search mode."""

    REGEX = "regex"
    BM25 = "bm25"
    JARO_WINKLER = "jaro_winkler"


@dataclass
class ConnectionResult:
    """Result of a database connection test."""

    connected: bool
    message: str


def tokenize(text: str) -> list[str]:
    """Tokenize text by splitting on common separators and filtering empty tokens."""
    return [token.lower() for token in re.split(r"[/._\s-]+", text) if token]


def search_items_regex(item_names: list[str], pattern: str, limit: int) -> list[str]:
    """Search items using regex pattern."""
    regex = re.compile(pattern)
    return [name for name in item_names if regex.search(name)][:limit]


def search_items_jaro_winkler(item_names: list[str], pattern: str, limit: int) -> list[str]:
    """Search items using Jaro-Winkler similarity."""
    tokenized_pattern = " ".join(tokenize(pattern))
    similarities = [(name, jaro_winkler_similarity(" ".join(tokenize(name)), tokenized_pattern)) for name in item_names]
    return [name for name, _ in sorted(similarities, key=lambda x: x[1], reverse=True)][:limit]


def search_items_bm25(item_names: list[str], pattern: str, limit: int) -> list[str]:
    """Search items using BM25 ranking algorithm."""
    query_tokens = tokenize(pattern)
    if not query_tokens:
        return []

    valid_items = [(name, tokenize(name)) for name in item_names]
    valid_items = [(name, tokens) for name, tokens in valid_items if tokens]
    if not valid_items:
        return []

    # Create corpus of tokenized item names
    corpus = [tokens for _, tokens in valid_items]

    # Initialize BM25 with the corpus
    bm25 = BM25Okapi(corpus)

    # Get BM25 scores for the query
    scores = bm25.get_scores(query_tokens)

    return [
        name
        for name, _ in sorted(zip([n for n, _ in valid_items], scores, strict=False), key=lambda x: x[1], reverse=True)
    ][:limit]


def search_items(
    item_names: list[str], pattern: str, mode: SearchMode = SearchMode.REGEX, limit: int = 10
) -> list[str]:
    """Search for item names using different algorithms."""
    if not item_names:
        return []

    if mode == SearchMode.REGEX:
        return search_items_regex(item_names, pattern, limit)
    elif mode == SearchMode.JARO_WINKLER:
        return search_items_jaro_winkler(item_names, pattern, limit)
    elif mode == SearchMode.BM25:
        return search_items_bm25(item_names, pattern, limit)
    else:
        raise NotImplementedError(f"Unknown search mode: {mode}")


def serialize_value(v: Any) -> Any:
    """Serialize individual values, handling special types like datetime and NaN."""
    # Convert pandas and Python datetime objects to ISO format, handle NaT/NaN
    if pd.isna(v):
        return None
    if isinstance(v, datetime | pd.Timestamp):
        return v.isoformat()
    if isinstance(v, pd.Period):
        return v.asfreq("D").to_timestamp().isoformat()
    elif not hasattr(v, "__dict__"):
        return str(v)
    return v


def serialize_dict(d: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a dictionary to a JSON-serializable response format with truncation.

    Serializes dictionary data and handles automatic truncation when the string
    representation exceeds MAX_DATA_CHARS.

    Args:
        d: The dictionary to convert and format

    Returns:
        Dictionary with 'data' (original or truncated dict), 'char_count' (total characters),
        and optional 'message' (truncation notice when data is truncated)
    """
    # Convert dict to string to check length
    dict_str = str(d)
    total_chars = len(dict_str)

    # Handle truncation if needed
    is_truncated = total_chars > MAX_DATA_CHARS
    dict_value = d if not is_truncated else dict_str[:MAX_DATA_CHARS] + "..."

    result = {
        "data": dict_value,
        "type": "dict",
    }

    if is_truncated:
        result["message"] = (
            f"Results truncated to {MAX_DATA_CHARS} characters (showing {MAX_DATA_CHARS} of {total_chars} total characters)"
        )

    return result


def serialize_response(response: Any) -> dict[str, Any]:
    """
    Serialize any response type to a JSON-serializable format.
    - Handles pandas DataFrames using serialize_dataframe.
    - Handles dictionaries using serialize_dict for truncation.
    - For other types, attempts to use Pydantic's TypeAdapter for robust, compact serialization.
    - Falls back to string conversion if serialization fails.

    Args:
        response: Any response type from tools

    Returns:
        Dictionary with serialized response data and type information.
    """
    # Handle pandas DataFrames specifically
    if isinstance(response, pd.DataFrame):
        return serialize_dataframe(response)
    elif isinstance(response, dict):
        return serialize_dict(response)
    else:
        try:
            # Use Pydantic's TypeAdapter for robust serialization of most types
            data = TypeAdapter(type(response)).dump_python(response)
        except Exception:
            # Fallback: convert to string if serialization fails
            data = str(response)
        return {"data": data, "type": type(response).__name__}


def serialize_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """
    Convert a pandas DataFrame to a JSON-serializable response format with pagination.

    Serializes DataFrame data including datetime objects and handles automatic truncation
    when the dataset exceeds MAX_DATA_ROWS.

    Args:
        df: The pandas DataFrame to convert and format

    Returns:
        Dictionary with 'data' (table structure), 'row_count' (total rows), and
        optional 'message' (truncation notice when data is truncated)
    """

    # Build rows including index, serializing each cell
    rows_with_indices = []
    for idx, row in df.iterrows():
        serialized_row = [serialize_value(idx)]
        for v in row.tolist():
            serialized_row.append(serialize_value(v))
        rows_with_indices.append(serialized_row)

    columns_with_index = ["index"] + df.columns.tolist()

    # Get total row count
    total_rows = len(rows_with_indices)

    # Handle truncation if needed
    is_truncated = total_rows > MAX_DATA_ROWS
    if is_truncated:
        rows_with_indices = rows_with_indices[:MAX_DATA_ROWS]

    table_data = {
        "type": "table",
        "columns": columns_with_index,
        "rows": rows_with_indices,
    }

    result = {"data": table_data, "row_count": total_rows}

    if is_truncated:
        result["message"] = (
            f"Results truncated to {MAX_DATA_ROWS} rows (showing {MAX_DATA_ROWS} of {total_rows} total rows)"
        )

    return result
