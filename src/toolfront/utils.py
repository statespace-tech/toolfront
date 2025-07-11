import json
import logging
import re
from typing import Any

import pandas as pd
from jellyfish import jaro_winkler_similarity
from pydantic import TypeAdapter
from rank_bm25 import BM25Okapi

from toolfront.config import MAX_DATA_CHARS, MAX_DATA_ROWS
from toolfront.types import SearchMode

logger = logging.getLogger("toolfront")
logger.setLevel(logging.INFO)


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
        for name, score in sorted(
            zip([n for n, _ in valid_items], scores, strict=False), key=lambda x: x[1], reverse=True
        )
        if score > 0
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


def serialize_response(response: Any) -> dict[str, Any]:
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
        json_str = response.to_csv(index=False)
        return {"data": json_str}

    # For all other types, use pydantic TypeAdapter
    adapter = TypeAdapter(Any)
    serialized = adapter.dump_python(response)

    # Convert to JSON string to check character count
    json_str = json.dumps(serialized)

    # Handle truncation
    if len(json_str) > MAX_DATA_CHARS:
        truncated_str = json_str[: MAX_DATA_CHARS - 3] + "..."
        return {
            "data": truncated_str,
            "truncation_message": f"Showing {len(truncated_str):,} characters of {len(json_str):,} total characters",
        }

    return {"data": serialized}
