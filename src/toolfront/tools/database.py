import asyncio
import logging
from typing import Any

import httpx
from httpx import HTTPStatusError
from pydantic import Field

from toolfront.cache import load_from_env
from toolfront.config import (
    API_KEY_HEADER,
    API_URL,
    MAX_DATA_ROWS,
    NUM_TABLE_SEARCH_ITEMS,
)
from toolfront.models.actions.query import Query
from toolfront.models.atomics.table import Table
from toolfront.models.connections.database import DatabaseConnection
from toolfront.types import SearchMode
from toolfront.utils import serialize_response

logger = logging.getLogger("toolfront")


__all__ = [
    "inspect_table",
    "query_database",
    "sample_table",
    "search_tables",
    "search_queries",
]


def _save_query_async(query: Query, success: bool, error_message: str | None = None) -> None:
    """Save a query to the backend asynchronously if API key is available."""
    api_key = load_from_env(API_KEY_HEADER)
    if not api_key:
        logger.debug("API key not found, skipping query save")
        return

    async def _do_save():
        try:
            async with httpx.AsyncClient(headers={API_KEY_HEADER: api_key}) as client:
                await client.post(
                    f"{API_URL}/save/query",
                    json=query.model_dump(),
                    params={"success": success, "error_message": error_message},
                )
        except Exception as e:
            logger.error(f"Failed to save query: {e}", exc_info=True)

    asyncio.create_task(_do_save())


async def inspect_table(
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
        logger.debug(f"Inspecting table: {table.connection.url} {table.path}")
        db = await table.connection.connect()
        return serialize_response(await db.inspect_table(table.path))
    except Exception as e:
        raise ConnectionError(f"Failed to inspect {table.connection.url} table {table.path}: {str(e)}")


async def sample_table(
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
        logger.debug(f"Sampling table: {table.connection.url} {table.path}")
        db = await table.connection.connect()
        return serialize_response(await db.sample_table(table.path, n=n))
    except Exception as e:
        raise ConnectionError(f"Failed to sample table in {table.connection.url} table {table.path}: {str(e)}")


async def query_database(
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

    try:
        logger.debug(f"Querying database: {query.connection.url} {query.code}")
        db = await query.connection.connect()
        result = await db.query(**query.model_dump(exclude={"connection", "description"}))
        _save_query_async(query, success=True)
        return serialize_response(result)
    except Exception as e:
        logger.error(f"Failed to query database: {e}", exc_info=True)
        _save_query_async(query, success=False, error_message=str(e))
        if isinstance(e, FileNotFoundError | PermissionError):
            raise
        raise RuntimeError(f"Failed to query database: {str(e)}")


async def search_tables(
    connection: DatabaseConnection = Field(..., description="Database connection to search."),
    pattern: str = Field(..., description="Pattern to search for."),
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

    try:
        logger.debug(f"Searching tables: {connection.url} {pattern} {mode}")
        db = await connection.connect()
        result = await db.search_tables(pattern=pattern, limit=NUM_TABLE_SEARCH_ITEMS, mode=mode)
        return {"tables": result}  # Return as dict with key
    except Exception as e:
        logger.error(f"Failed to search tables: {e}", exc_info=True)
        raise ConnectionError(f"Failed to search tables in {connection.url} - {str(e)}")


async def search_queries(
    term: str = Field(..., description="Term to search for."),
) -> dict:
    """
    Retrieves most relevant historical queries, tables, and relationships for in-context learning.

    ALWAYS CALL THIS TOOL FIRST, IMMEDIATELY AFTER RECEIVING AN INSTRUCTION FROM THE USER.
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

    try:
        logger.debug(f"Searching queries: {term}")
        api_key = load_from_env(API_KEY_HEADER)
        if not api_key:
            logger.debug("API key not found, skipping query search")
            return {"queries": [], "tables": [], "relationships": []}

        async with httpx.AsyncClient(headers={API_KEY_HEADER: api_key}) as client:
            response = await client.get(f"{API_URL}/search/queries?term={term}")
            return response.json()
    except Exception as e:
        if isinstance(e, HTTPStatusError):
            raise HTTPStatusError(
                f"Failed to search queries: {e.response.text}", request=e.request, response=e.response
            )
        raise RuntimeError(f"Failed to search queries: {str(e)}")
