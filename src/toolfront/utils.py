"""
Data serialization utilities for converting DataFrames and other data structures.
"""

import logging
import re
from datetime import datetime
from typing import Any
from urllib.parse import parse_qs, urlparse, urlunparse

import pandas as pd
from jellyfish import jaro_winkler_similarity
from pydantic import BaseModel, Field
from rank_bm25 import BM25Okapi

from toolfront.config import MAX_DATA_ROWS
from toolfront.types import SearchMode

logger = logging.getLogger("toolfront")
logger.setLevel(logging.INFO)


class APIURLParseResult(BaseModel):
    """Result of API URL parsing."""

    url: str = Field(description="The base URL (with server URL from spec if available)")
    openapi_spec: dict[str, Any] | None = Field(default=None, description="The OpenAPI specification")
    query_params: dict[str, Any] = Field(default_factory=dict, description="Regular query parameters")
    auth_headers: dict[str, Any] = Field(default_factory=dict, description="Authentication headers")
    auth_query_params: dict[str, Any] = Field(default_factory=dict, description="Authentication query parameters")


def parse_api_url(url: str, spec: dict[str, Any] | None = None) -> APIURLParseResult:
    """Parse an API URL and extract authentication and query parameters.

    Args:
        url: The URL to parse
        spec: Optional OpenAPI specification

    Returns:
        APIURLParseResult containing:
            - url: The base URL (with server URL from spec if available)
            - openapi_spec: The OpenAPI specification
            - query_params: Regular query parameters
            - auth_headers: Authentication headers
            - auth_query_params: Authentication query parameters
    """
    parsed = urlparse(url)

    # Get server URL from spec or construct from parsed URL
    servers = spec.get("servers", []) if spec else []
    server_url = servers[0].get("url", None) if servers else None

    if server_url is None:
        final_url = f"{parsed.scheme}://{parsed.netloc}"
    else:
        # If the API URL is a relative path, prepend the parsed URL
        final_url = server_url if server_url.startswith("http") else f"https://{parsed.netloc}{server_url}"

    # Parse query parameters
    query_params = parse_qs(parsed.query)
    # Convert from lists to single values
    query_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}

    # Initialize auth containers
    auth_headers = {}
    auth_query_params = {}

    # Common auth parameter names
    auth_param_names = ["apikey", "api_key", "token", "access_token", "bearer", "key", "auth"]

    # Check OpenAPI spec for security schemes
    if spec and "components" in spec and "securitySchemes" in spec["components"]:
        for _scheme_name, scheme in spec["components"]["securitySchemes"].items():
            if scheme.get("type") == "apiKey":
                param_name = scheme.get("name")
                param_location = scheme.get("in", "query")

                # Find matching parameter in query params (case-insensitive)
                for qp_name, qp_value in list(query_params.items()):
                    if qp_name.lower() == param_name.lower():
                        if param_location == "header":
                            auth_headers[param_name] = qp_value
                            del query_params[qp_name]
                        elif param_location == "query":
                            auth_query_params[qp_name] = qp_value
                            del query_params[qp_name]
                        break
            elif scheme.get("type") == "http" and scheme.get("scheme") == "bearer":
                # Look for bearer/token in query params
                for qp_name, qp_value in list(query_params.items()):
                    if qp_name.lower() in ["bearer", "token", "access_token"]:
                        auth_headers["Authorization"] = f"Bearer {qp_value}"
                        del query_params[qp_name]
                        break
    else:
        # No spec or security schemes - use heuristics
        for qp_name, qp_value in list(query_params.items()):
            if qp_name.lower() in auth_param_names:
                if qp_name.lower() in ["bearer", "token", "access_token"]:
                    auth_headers["Authorization"] = f"Bearer {qp_value}"
                    del query_params[qp_name]
                else:
                    # Default to keeping in query params (like Polygon)
                    auth_query_params[qp_name] = qp_value
                    del query_params[qp_name]

    return APIURLParseResult(
        url=final_url,
        openapi_spec=spec,
        query_params=query_params,
        auth_headers=auth_headers,
        auth_query_params=auth_query_params,
    )


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
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"
        return urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
    return url


def tokenize(text: str) -> list[str]:
    """Tokenize text into words."""
    return re.findall(r"\w+", text.lower())


def search_items_regex(item_names: list[str], pattern: str, limit: int) -> list[str]:
    """Search items using regex."""
    try:
        regex = re.compile(pattern, re.IGNORECASE)
        return [name for name in item_names if regex.search(name)][:limit]
    except re.error:
        return []


def search_items_jaro_winkler(item_names: list[str], pattern: str, limit: int) -> list[str]:
    """Search items using Jaro-Winkler similarity."""
    scores = [(name, jaro_winkler_similarity(pattern.lower(), name.lower())) for name in item_names]
    return [name for name, score in sorted(scores, key=lambda x: x[1], reverse=True) if score > 0.8][:limit]


def search_items_bm25(item_names: list[str], pattern: str, limit: int) -> list[str]:
    """Search items using BM25."""
    # Tokenize all items
    tokenized_items = [tokenize(name) for name in item_names]

    # Create BM25 model
    bm25 = BM25Okapi(tokenized_items)

    # Tokenize query and get scores
    query_tokens = tokenize(pattern)
    if not query_tokens:
        return []

    # Get scores and sort
    scores = bm25.get_scores(query_tokens)
    scored_items = list(zip(item_names, scores, strict=False))
    return [name for name, score in sorted(scored_items, key=lambda x: x[1], reverse=True) if score > 0][:limit]


def search_items(
    item_names: list[str], pattern: str, mode: SearchMode = SearchMode.REGEX, limit: int = 10
) -> list[str]:
    """
    Search items using different algorithms.

    Args:
        item_names: List of item names to search
        pattern: Search pattern
        mode: Search mode (regex, bm25, jaro_winkler)
        limit: Maximum number of results to return

    Returns:
        List of matching item names
    """
    if mode == SearchMode.REGEX:
        return search_items_regex(item_names, pattern, limit)
    elif mode == SearchMode.BM25:
        return search_items_bm25(item_names, pattern, limit)
    elif mode == SearchMode.JARO_WINKLER:
        return search_items_jaro_winkler(item_names, pattern, limit)
    else:
        raise ValueError(f"Invalid search mode: {mode}")


def serialize_value(v: Any) -> Any:
    """Serialize a single value."""
    if pd.isna(v):
        return None
    elif isinstance(v, (int, float, str, bool)):
        return v
    elif isinstance(v, datetime):
        return v.isoformat()
    else:
        return str(v)


def serialize_dict(d: dict[str, Any]) -> dict[str, Any]:
    """
    Serialize a dictionary to JSON-compatible format.

    Args:
        d: Dictionary to serialize

    Returns:
        Serialized dictionary
    """
    result = {}
    for k, v in d.items():
        if isinstance(v, dict):
            result[k] = serialize_dict(v)
        elif isinstance(v, (list, tuple)):
            result[k] = [serialize_value(x) for x in v]
        else:
            result[k] = serialize_value(v)
    return result


def serialize_response(response: Any) -> dict[str, Any]:
    """
    Serialize a response to JSON-compatible format.

    Args:
        response: Response to serialize

    Returns:
        Serialized response
    """
    if isinstance(response, pd.DataFrame):
        return serialize_dataframe(response)
    elif isinstance(response, dict):
        return serialize_dict(response)
    elif isinstance(response, (list, tuple)):
        return [serialize_value(x) for x in response]
    else:
        return serialize_value(response)


def serialize_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """
    Serialize a DataFrame to JSON-compatible format.

    Args:
        df: DataFrame to serialize

    Returns:
        Serialized DataFrame with:
            - columns: List of column names
            - data: List of rows
            - truncated: Whether the data was truncated
    """
    # Get column names and types
    columns = [{"name": str(col), "type": str(dtype)} for col, dtype in df.dtypes.items()]

    # Convert to records
    truncated = False
    if len(df) > MAX_DATA_ROWS:
        df = df.head(MAX_DATA_ROWS)
        truncated = True

    # Convert to list of dicts
    data = df.to_dict("records")

    # Serialize each value
    data = [serialize_dict(row) for row in data]

    return {
        "columns": columns,
        "data": data,
        "truncated": truncated,
    }
