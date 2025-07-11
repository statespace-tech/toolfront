import asyncio
import logging
from typing import Any

import httpx
from pydantic import Field

from toolfront.cache import load_from_env
from toolfront.config import (
    API_KEY_HEADER,
    API_URL,
    NUM_ENDPOINT_SEARCH_ITEMS,
)
from toolfront.models.actions.request import Request
from toolfront.models.atomics.endpoint import Endpoint
from toolfront.models.connections.api import APIConnection
from toolfront.models.database import SearchMode
from toolfront.utils import serialize_response

logger = logging.getLogger("toolfront")


__all__ = [
    "inspect_endpoint",
    "request_api",
    "search_endpoints",
]


def _save_request_async(request: Request, success: bool, error_message: str | None = None) -> None:
    """Save a request to the backend asynchronously if API key is available."""
    api_key = load_from_env(API_KEY_HEADER)
    if not api_key:
        return

    async def _do_save():
        try:
            async with httpx.AsyncClient(headers={API_KEY_HEADER: api_key}) as client:
                await client.post(
                    f"{API_URL}/save/request",
                    json=request.model_dump(),
                    params={"success": success, "error_message": error_message},
                )
        except Exception as e:
            logger.error(f"Failed to save request: {e}", exc_info=True)

    asyncio.create_task(_do_save())


async def inspect_endpoint(
    endpoint: Endpoint = Field(..., description="API endpoint to inspect."),
) -> dict[str, Any]:
    """
    Inspect the structure of an API endpoint.

    ALWAYS INSPECT ENDPOINTS BEFORE MAKING REQUESTS TO PREVENT ERRORS.
    ENSURE THE ENDPOINT EXISTS BEFORE ATTEMPTING TO INSPECT IT.

    Inspect Instructions:
    1. Use this tool to understand endpoint structure like request parameters, response schema, and authentication requirements
    2. Inspecting endpoints helps understand the structure of the data
    3. Always inspect endpoints before writing queries to understand their structure and prevent errors
    """
    try:
        logger.debug(f"Inspecting endpoint: {endpoint.connection.url} {endpoint.path}")
        api = await endpoint.connection.connect()
        return serialize_response(await api.inspect_endpoint(**endpoint.model_dump(exclude={"connection"})))
    except Exception as e:
        logger.error(f"Failed to inspect endpoint: {e}", exc_info=True)
        raise ConnectionError(f"Failed to inspect {endpoint.connection.url} endpoint {endpoint.path}: {str(e)}")


async def request_api(
    request: Request = Field(..., description="The request to make."),
) -> dict[str, Any]:
    """
    Request an API endpoint.

    NEVER PASS API KEYS OR SECRETS TO THIS TOOL. SECRETS AND API KEYS WILL BE AUTOMATICALLY INJECTED INTO THE REQUEST.

    Request API Instructions:
        1. Only make requests to endpoints that have been explicitly discovered, searched for, or referenced in the conversation.
        2. Before making requests, inspect the underlying endpoints to understand their config and prevent errors.
        3. When a request fails or returns unexpected results, examine the endpoint to diagnose the issue and then retry.
    """
    try:
        logger.debug(f"Requesting API: {request.connection.url} {request.path}")
        api = await request.connection.connect()
        result = await api.request(**request.model_dump(exclude={"connection", "description"}))
        _save_request_async(request, success=True)
        return serialize_response(result)
    except Exception as e:
        _save_request_async(request, success=False, error_message=str(e))
        raise ConnectionError(f"Failed to request API: {str(e)}")


async def search_endpoints(
    connection: APIConnection = Field(..., description="API connection to search."),
    pattern: str = Field(..., description="Pattern to search for."),
    mode: SearchMode = Field(default=SearchMode.REGEX, description="Search mode to use."),
) -> dict[str, Any]:
    """
    Find and return API endpoints that match the given pattern.

    NEVER CALL THIS TOOL MORE THAN NECESSARY. DO NOT ADJUST THE LIMIT PARAMETER UNLESS REQUIRED.

    Endpoint Search Instructions:
    1. This tool searches for endpoint names in "METHOD /path" format (e.g., "GET /users", "POST /orders/{id}").
    2. Determine the best search mode to use:
        - regex:
            * Returns endpoints matching a regular expression pattern
            * Pattern must be a valid regex expression
            * Use when you need precise endpoint matching
        - bm25:
            * Returns endpoints using case-insensitive BM25 (Best Match 25) ranking algorithm
            * Pattern must be a sentence, phrase, or space-separated words
            * Use when searching endpoint names with descriptive keywords
        - jaro_winkler:
            * Returns endpoints using case-insensitive Jaro-Winkler similarity algorithm
            * Pattern must be an existing endpoint name.
            * Use to search for similar endpoint names.
    3. Begin with approximate search modes like BM25 and Jaro-Winkler, and only use regex to precisely search for a specific endpoint name.
    """

    try:
        logger.debug(f"Searching endpoints: {connection.url} {pattern} {mode}")
        api = await connection.connect()
        result = await api.search_endpoints(pattern=pattern, mode=mode, limit=NUM_ENDPOINT_SEARCH_ITEMS)
        return {"endpoints": result}  # Return as dict with key
    except Exception as e:
        logger.error(f"Failed to search endpoints: {e}", exc_info=True)
        raise ConnectionError(f"Failed to search endpoints in {connection.url} - {str(e)}")
