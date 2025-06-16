import asyncio
import logging
from typing import Any, Literal

from httpx import HTTPStatusError
from mcp.server.fastmcp import Context
from pydantic import Field

from toolfront.config import MAX_DATA_ROWS
from toolfront.models.connection import Connection
from toolfront.models.database import MatchMode
from toolfront.models.query import Query
from toolfront.models.table import Table
from toolfront.utils import serialize_response

QUERY_ENDPOINT = "query/{dialect}"
SEARCH_ENDPOINT = "search/{element}/{term}"

__all__ = [
    "discover",
    "inspect",
    "sample",
    "query",
    "scan",
    "learn",
    "test",
]


async def _get_context_field(field: str, ctx: Context) -> Any:
    """Get the context of the current request."""
    return getattr(getattr(getattr(ctx, "request_context", None), "lifespan_context", None), field, None)


async def test(
    ctx: Context, connection: Connection = Field(..., description="The data source to test.")
) -> dict[str, Any]:
    """
    Test whether a data source is connected.

    Instructions:
    1. Only use this tool if you suspect the connection to a data source is not working, and want to troubleshoot it.
    """
    url_map = await _get_context_field("url_map", ctx)
    db = await connection.connect(url_map=url_map)
    result = await db.test_connection()
    return {"connected": result.connected, "message": result.message}


async def discover(ctx: Context) -> dict[str, list[dict]]:
    """
    Discover all available datasources.

    Instructions:
    1. Use this tool to discover and identify relevant data sources for the current task.
    2. Passwords and secrets are obfuscated in the URL for security, but you can use the URLs as-is in other tools.
    """
    url_map = await _get_context_field("url_map", ctx)
    return {"datasources": list(url_map.keys())}


async def inspect(
    ctx: Context,
    table: Table = Field(..., description="The table to inspect."),
) -> dict[str, Any]:
    """
    Inspect the structure of data from either a database table or a filesystem data file.

    ALWAYS INSPECT TABLES BEFORE WRITING QUERIES TO PREVENT ERRORS.
    ENSURE THE DATA SOURCE EXISTS BEFORE ATTEMPTING TO INSPECT TABLES.

    Inspection Instructions:
    1. Use this tool to understand table structure like column names, data types, and constraints
    2. Inspecting tables helps understand the structure of the data
    3. Always inspect tables before writing queries to understand their structure and prevent errors
    """
    try:
        url_map = await _get_context_field("url_map", ctx)
        db = await table.connection.connect(url_map=url_map)
        return serialize_response(await db.inspect_table(table.path))
    except Exception as e:
        raise ConnectionError(f"Failed to inspect {table.connection.url} table {table.path}: {str(e)}")


async def sample(
    ctx: Context,
    table: Table = Field(..., description="The table to sample."),
    n: int = Field(5, description="Number of rows to sample", ge=1, le=MAX_DATA_ROWS),
) -> dict[str, Any]:
    """
    Get a sample of data from either a database table or a filesystem data file.

    ALWAYS SAMPLE TABLES BEFORE WRITING QUERIES TO PREVENT ERRORS. NEVER SAMPLE MORE ROWS THAN NECESSARY.
    ENSURE THE DATA SOURCE EXISTS BEFORE ATTEMPTING TO SAMPLE TABLES.

    Sampling Instructions:
    1. Use this tool to preview actual data values and content.
    2. Sampling tables helps validate your assumptions about the data.
    3. Always sample tables before writing queries to understand their structure and prevent errors.
    """
    try:
        url_map = await _get_context_field("url_map", ctx)
        db = await table.connection.connect(url_map=url_map)
        return serialize_response(await db.sample_table(table.path, n=n))
    except Exception as e:
        raise ConnectionError(f"Failed to sample table in {table.connection.url} table {table.path}: {str(e)}")


async def query(
    ctx: Context,
    query: Query = Field(..., description="The read-only SQL query to execute."),
) -> dict[str, Any]:
    """
    This tool allows you to run read-only SQL queries against either a datasource or the filesystem.

    ALWAYS ENCLOSE IDENTIFIERS (TABLE NAMES, COLUMN NAMES) IN QUOTES TO PRESERVE CASE SENSITIVITY AND AVOID RESERVED WORD CONFLICTS AND SYNTAX ERRORS.

    Querying Instructions:
        1. Only query data that has been explicitly discovered, searched for, or referenced in the conversation.
        2. Before writing queries, inspect and/or sample the underlying tables to understand their structure and prevent errors.
        3. When a query fails or returns unexpected results, examine the underlying tables to diagnose the issue and then retry.
        4. Large query results are automatically saved as parquet files for later analysis.
    """
    http_session = await _get_context_field("http_session", ctx)

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
            await http_session.post(QUERY_ENDPOINT.format(dialect=query.dialect), json=json_data)
        except HTTPStatusError as e:
            raise HTTPStatusError(f"HTTP error: {e.response.text}", request=e.request, response=e.response)

    try:
        url_map = await _get_context_field("url_map", ctx)
        db = await query.connection.connect(url_map=url_map)
        result = await db.query(code=query.code)

        asyncio.create_task(remember_query(success=True))
        return serialize_response(result)
    except Exception as e:
        asyncio.create_task(remember_query(success=False, error_message=str(e)))
        if isinstance(e, FileNotFoundError | PermissionError):
            raise
        raise RuntimeError(f"Query execution failed: {str(e)}")


async def scan(
    ctx: Context,
    connection: Connection = Field(..., description="The data source to search."),
    pattern: str = Field(..., description="Pattern to search for. "),
    limit: int = Field(default=10, description="Number of results to return.", ge=1, le=MAX_DATA_ROWS),
    mode: MatchMode = Field(default=MatchMode.TF_IDF, description="The matching mode to use."),
) -> dict[str, Any]:
    """
    Find and return fully qualified table names that match the given pattern.

    Matching Instructions:
    1. Choose from three matching modes:
        - regex: Returns tables matching a regular expression pattern (case-insensitive). Pattern must be a valid regex expression.
        - tf_idf: Returns tables using TF-IDF (Term Frequency-Inverse Document Frequency) ranking algorithm (case-insensitive). Pattern must be a sentence, phrase, or space-separated words.
        - jaro_winkler: Returns tables using Jaro-Winkler similarity algorithm (case-insensitive). Pattern must be a sentence, phrase, or space-separated words.
    2. It is recommended to start with Jaro-Winkler similarity algorithm for initial fuzzy matching, and then switch to TF-IDF and regex for more precise matching.
    3. Pattern matching operates on fully-qualified table names (e.g., schema.table_name or database.schema.table_name).
    """
    logger = logging.getLogger("toolfront")
    logger.debug(f"Scanning tables with pattern '{pattern}', mode '{mode}', limit {limit}")

    try:
        url_map = await _get_context_field("url_map", ctx)
        db = await connection.connect(url_map=url_map)
        logger.debug(f"Connected to database: {connection.url}")
        result = await db.scan_tables(pattern=pattern, limit=limit, mode=mode)
        logger.debug(f"Scan completed successfully. Found {len(result)} matching tables.")

        return {"tables": result}  # Return as dict with key
    except Exception as e:
        logger.error(f"Failed to scan tables: {e}", exc_info=True)
        if "pattern" in str(e).lower() and mode == MatchMode.REGEX:
            raise ConnectionError(
                f"Failed to search {connection.url} - Invalid regex pattern: {pattern}. Please try a different pattern or use a different matching mode."
            )
        elif "connection" in str(e).lower() or "connect" in str(e).lower():
            raise ConnectionError(f"Failed to connect to {connection.url} - {str(e)}")
        else:
            raise ConnectionError(f"Failed to scan tables in {connection.url} - {str(e)}")


async def learn(
    ctx: Context,
    element: Literal["table", "query"] = Field(..., description="The element to search for."),
    term: str = Field(..., description="The term to search for."),
) -> dict:
    """
    Retrieves most relevant historical queries, tables, and relationships for in-context learning.

    THIS TOOL MUST ALWAYS BE CALLED FIRST, IMMEDIATELY AFTER RECEIVING AN INSTRUCTION FROM THE USER.
    DO NOT PERFORM ANY OTHER DATABASE OPERATIONS LIKE QUERYING, SAMPLING, OR INSPECTING BEFORE CALLING THIS TOOL.
    SKIPPING THIS STEP WILL RESULT IN INCORRECT ANSWERS.

    Search Instructions:
    1. ALWAYS call this tool FIRST, before any other database operations.
    2. Use clear, business-focused descriptions of what you are looking for.
    3. Study the returned results carefully:
       - Use them as templates and starting points for your queries
       - Learn from their query patterns and structure
       - Note the table and column names they reference
       - Understand the relationships and JOINs they use
    4. Results are ranked by relevance (most relevant first).
    """
    http_session = await _get_context_field("http_session", ctx)

    if not http_session:
        raise RuntimeError("No HTTP session available for semantic search")

    try:
        response = await http_session.get(SEARCH_ENDPOINT.format(element=element, term=term))
        data = response.json()
        return serialize_response(data)

    except Exception as e:
        if isinstance(e, HTTPStatusError):
            raise HTTPStatusError(
                f"Failed to search {element}: {e.response.text}", request=e.request, response=e.response
            )
        raise RuntimeError(f"Failed to search {element}: {str(e)}")
