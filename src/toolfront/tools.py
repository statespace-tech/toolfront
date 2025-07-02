import asyncio
import logging
from typing import Any

from httpx import HTTPStatusError
from mcp.server.fastmcp import Context
from pydantic import Field

from toolfront.config import MAX_DATA_ROWS, NUM_ENDPOINT_SEARCH_ITEMS, NUM_QUERY_SEARCH_ITEMS, NUM_TABLE_SEARCH_ITEMS
from toolfront.models.connection import APIConnection, DatabaseConnection
from toolfront.models.database import SearchMode
from toolfront.models.endpoint import Endpoint
from toolfront.models.query import Query
from toolfront.models.request import Request
from toolfront.models.table import Table
from toolfront.utils import serialize_response

__all__ = [
    "discover",
    "inspect_table",
    "query_database",
    "request_api",
    "sample_table",
    "search_tables",
    "search_endpoints",
    "search_queries",
]


def _get_context_field(field: str, ctx: Context) -> Any:
    """Get the context of the current request."""
    return getattr(getattr(getattr(ctx, "request_context", None), "lifespan_context", None), field, None)


def _get_url_objects(ctx: Context) -> list:
    """Get the list of URL objects from context."""
    return _get_context_field("url_objects", ctx) or []


def _get_metadata_map(ctx: Context) -> dict:
    """Get the metadata map from context."""
    return _get_context_field("metadata_map", ctx) or {}


async def _resolve_connection_if_needed(
    connection: DatabaseConnection | APIConnection, ctx: Context
) -> DatabaseConnection | APIConnection:
    """Resolve display URLs back to actual connection objects if needed."""
    # Always try to resolve by matching display strings to original URLs
    display_str = str(connection.url)
    url_objects = _get_url_objects(ctx)
    metadata_map = _get_metadata_map(ctx)

    for url_obj in url_objects:
        if url_obj.matches_display_string(display_str):
            if isinstance(connection, DatabaseConnection):
                return DatabaseConnection(url=url_obj)
            elif isinstance(connection, APIConnection):
                # For API connections, we need to pass the OpenAPI spec too
                api_connection = APIConnection(url=url_obj)
                # Store metadata for later use by the API object
                metadata = metadata_map.get(str(url_obj), {})
                api_connection._metadata = metadata  # Store metadata on the connection
                return api_connection

    return connection


async def discover(ctx: Context) -> dict[str, list[dict]]:
    """
    Discover all available datasources.

    Discover Instructions:
    1. Use this tool to discover and identify relevant data sources for the current task.
    2. Passwords and secrets are obfuscated in the URL for security, but you can use the URLs as-is in other tools.
    """
    try:
        url_objects = _get_url_objects(ctx)
        if url_objects is None:
            return {"datasources": ["ERROR: url_objects is None"]}
        if hasattr(url_objects, "__iter__"):
            return {"datasources": [str(url_obj) for url_obj in url_objects]}
        else:
            return {"datasources": [f"ERROR: url_objects is not iterable, type: {type(url_objects)}"]}
    except Exception as e:
        return {"datasources": [f"ERROR: {e}"]}


async def inspect_table(
    ctx: Context,
    table: Table = Field(..., description="Database table to inspect."),
) -> dict[str, Any]:
    """
    Inspect the structure of database table.

    ALWAYS INSPECT TABLES BEFORE WRITING QUERIES TO PREVENT ERRORS.
    ENSURE THE TABLE EXISTS BEFORE ATTEMPTING TO INSPECT IT.

    Inspect Instructions:
    1. Use this tool to understand table structure like column names, data types, and constraints
    2. Inspecting tables helps understand the structure of the data
    3. Always inspect tables before writing queries to understand their structure and prevent errors
    """
    try:
        # Resolve display URL if needed
        resolved_connection = await _resolve_connection_if_needed(table.connection, ctx)
        table.connection = resolved_connection
        db = await table.connection.connect(url_map={})
        return serialize_response(await db.inspect_table(table.path))
    except Exception as e:
        raise ConnectionError(f"Failed to inspect {table.connection.url} table {table.path}: {str(e)}")


async def inspect_endpoint(
    ctx: Context,
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
        # Resolve display URL if needed
        resolved_connection = await _resolve_connection_if_needed(endpoint.connection, ctx)
        api = await resolved_connection.connect(url_map={})
        return serialize_response(await api.inspect_endpoint(**endpoint.model_dump(exclude={"connection"})))
    except Exception as e:
        raise ConnectionError(f"Failed to inspect {resolved_connection.url} endpoint {endpoint.path}: {str(e)}")


async def sample_table(
    ctx: Context,
    table: Table = Field(..., description="Database table to sample."),
    n: int = Field(5, description="Number of rows to sample", ge=1, le=MAX_DATA_ROWS),
) -> dict[str, Any]:
    """
    Get a sample of data from a database table.

    ALWAYS SAMPLE TABLES BEFORE WRITING QUERIES TO PREVENT ERRORS. NEVER SAMPLE MORE ROWS THAN NECESSARY.
    ENSURE THE DATA SOURCE EXISTS BEFORE ATTEMPTING TO SAMPLE TABLES.

    Sample Instructions:
    1. Use this tool to preview actual data values and content.
    2. Sampling tables helps validate your assumptions about the data.
    3. Always sample tables before writing queries to understand their structure and prevent errors.
    """
    try:
        # Resolve display URL if needed
        resolved_connection = await _resolve_connection_if_needed(table.connection, ctx)
        table.connection = resolved_connection
        db = await table.connection.connect(url_map={})
        return serialize_response(await db.sample_table(table.path, n=n))
    except Exception as e:
        raise ConnectionError(f"Failed to sample table in {table.connection.url} table {table.path}: {str(e)}")


async def query_database(
    ctx: Context,
    query: Query = Field(..., description="Read-only SQL query to execute."),
) -> dict[str, Any]:
    """
    This tool allows you to run read-only SQL queries against a database.

    ALWAYS ENCLOSE IDENTIFIERS (TABLE NAMES, COLUMN NAMES) IN QUOTES TO PRESERVE CASE SENSITIVITY AND AVOID RESERVED WORD CONFLICTS AND SYNTAX ERRORS.

    Query Database Instructions:
        1. Only query tables that have been explicitly discovered, searched for, or referenced in the conversation.
        2. Always use the correct dialect for the database.
        3. Before writing queries, inspect and/or sample the underlying tables to understand their structure and prevent errors.
        4. When a query fails or returns unexpected results, examine the underlying tables to diagnose the issue and then retry.
    """
    http_session = _get_context_field("http_session", ctx)

    async def remember_query(success: bool, error_message: str | None = None) -> None:
        """Remember a query by its ID and description."""
        if not http_session:
            return

        try:
            json_data = {
                "code": query.code,
                "description": query.description,
                "success": success,
                "error_message": error_message,
            }
            await http_session.post(f"query/{query.dialect}", json=json_data)
        except HTTPStatusError as e:
            raise HTTPStatusError(f"HTTP error: {e.response.text}", request=e.request, response=e.response)

    try:
        # Resolve display URL if needed
        resolved_connection = await _resolve_connection_if_needed(query.connection, ctx)
        query.connection = resolved_connection
        db = await query.connection.connect(url_map={})
        result = await db.query(**query.model_dump(exclude={"connection", "description"}))
        asyncio.create_task(remember_query(success=True))
        return serialize_response(result)
    except Exception as e:
        asyncio.create_task(remember_query(success=False, error_message=str(e)))
        if isinstance(e, FileNotFoundError | PermissionError):
            raise
        raise RuntimeError(f"Query execution failed: {str(e)}")


async def request_api(
    ctx: Context,
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
        # Resolve display URL if needed
        resolved_connection = await _resolve_connection_if_needed(request.connection, ctx)
        api = await resolved_connection.connect(url_map={})
        result = await api.request(**request.model_dump(exclude={"connection", "description"}))
        return serialize_response(result)
    except Exception as e:
        if "DEBUG INFO" in str(e):
            raise e
        raise ConnectionError(f"Failed to request {resolved_connection.url} endpoint {request.path}: {str(e)}")


async def search_tables(
    ctx: Context,
    connection: DatabaseConnection = Field(..., description="Database connection to search."),
    pattern: str = Field(..., description="Pattern to search for. "),
    mode: SearchMode = Field(default=SearchMode.BM25, description="Search mode to use."),
) -> dict[str, Any]:
    """
    Find and return fully qualified table names that match the given pattern.

    NEVER CALL THIS TOOL MORE THAN NECESSARY. DO NOT ADJUST THE LIMIT PARAMETER UNLESS REQUIRED.

    Table Search Instructions:
    1. This tool searches for fully qualified table names in dot notation format (e.g., schema.table_name or database.schema.table_name).
    2. Determine the best search mode to use:
        - regex:
            * Returns tables matching a regular expression pattern
            * Pattern must be a valid regex expression
            * Use when you need precise table name matching
        - bm25:
            * Returns tables using case-insensitive BM25 (Best Match 25) ranking algorithm
            * Pattern must be a sentence, phrase, or space-separated words
            * Use when searching tables names with descriptive keywords
        - jaro_winkler:
            * Returns tables using case-insensitive Jaro-Winkler similarity algorithm
            * Pattern must be an existing table name.
            * Use to search for similar table names.
    3. Begin with approximate search modes like BM25 and Jaro-Winkler, and only use regex to precisely search for a specific table name.
    """
    logger = logging.getLogger("toolfront")
    logger.debug(f"Searching tables with pattern '{pattern}', mode '{mode}'")

    try:
        # Resolve display URL if needed
        resolved_connection = await _resolve_connection_if_needed(connection, ctx)
        connection = resolved_connection
        db = await connection.connect(url_map={})
        result = await db.search_tables(pattern=pattern, limit=NUM_TABLE_SEARCH_ITEMS, mode=mode)

        return {"tables": result}  # Return as dict with key
    except Exception as e:
        logger.error(f"Failed to search tables: {e}", exc_info=True)
        if "pattern" in str(e).lower() and mode == SearchMode.REGEX:
            raise ConnectionError(
                f"Failed to search {connection.url} - Invalid regex pattern: {pattern}. Please try a different pattern or use a different search mode."
            )
        elif "connection" in str(e).lower() or "connect" in str(e).lower():
            raise ConnectionError(f"Failed to connect to {connection.url} - {str(e)}")
        else:
            raise ConnectionError(f"Failed to search tables in {connection.url} - {str(e)}")


async def search_endpoints(
    ctx: Context,
    connection: APIConnection = Field(..., description="API connection to search."),
    pattern: str = Field(..., description="Pattern to search for. "),
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
    logger = logging.getLogger("toolfront")
    logger.debug(f"Searching endpoints with pattern '{pattern}', mode '{mode}'")

    try:
        # Resolve display URL if needed
        resolved_connection = await _resolve_connection_if_needed(connection, ctx)
        api = await resolved_connection.connect(url_map={})
        result = await api.search_endpoints(pattern=pattern, mode=mode, limit=NUM_ENDPOINT_SEARCH_ITEMS)

        return {"endpoints": result}  # Return as dict with key
    except Exception as e:
        logger.error(f"Failed to search endpoints: {e}", exc_info=True)
        if "pattern" in str(e).lower() and mode == SearchMode.REGEX:
            raise ConnectionError(
                f"Failed to search {resolved_connection.url} - Invalid regex pattern: {pattern}. Please try a different pattern or use a different search mode."
            )
        elif "connection" in str(e).lower() or "connect" in str(e).lower():
            raise ConnectionError(f"Failed to connect to {resolved_connection.url} - {str(e)}")
        else:
            raise ConnectionError(f"Failed to search endpoints in {resolved_connection.url} - {str(e)}")


async def search_queries(
    ctx: Context,
    term: str = Field(..., description="Term to search for."),
) -> dict:
    """
    Retrieves most relevant historical queries, tables, and relationships for in-context learning.

    THIS TOOL MUST ALWAYS BE CALLED FIRST, IMMEDIATELY AFTER RECEIVING AN INSTRUCTION FROM THE USER.
    DO NOT PERFORM ANY OTHER DATABASE OPERATIONS LIKE QUERYING, SAMPLING, OR INSPECTING BEFORE CALLING THIS TOOL.
    SKIPPING THIS STEP WILL RESULT IN INCORRECT ANSWERS.

    Learn Instructions:
    1. ALWAYS call this tool FIRST, before any other database operations.
    2. Use clear, business-focused descriptions of what you are looking for.
    3. Study the returned results carefully:
       - Use them as templates and starting points for your queries
       - Learn from their query patterns and structure
       - Note the table and column names they reference
       - Understand the relationships and JOINs they use
    """
    http_session = _get_context_field("http_session", ctx)

    if not http_session:
        raise RuntimeError("No HTTP session available for semantic search")

    try:
        response = await http_session.get(f"query/{term}?limit={NUM_QUERY_SEARCH_ITEMS}")
        data = response.json()
        return serialize_response(data)

    except Exception as e:
        if isinstance(e, HTTPStatusError):
            raise HTTPStatusError(
                f"Failed to search queries: {e.response.text}", request=e.request, response=e.response
            )
        raise RuntimeError(f"Failed to search queries: {str(e)}")
