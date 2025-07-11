import asyncio
import logging
from typing import Literal

import click
from mcp.server.fastmcp import FastMCP

from toolfront.cache import get_datasource_type, save_connections, save_to_env
from toolfront.config import API_KEY_HEADER
from toolfront.types import DatasourceType

logger = logging.getLogger("toolfront")
logger.setLevel(logging.INFO)

logging.info("Starting ToolFront MCP server")


async def get_mcp(urls: tuple[str, ...], api_key: str | None = None) -> FastMCP:
    clean_urls = await save_connections(urls)

    if api_key:
        save_to_env(API_KEY_HEADER, api_key)

    mcp = FastMCP("ToolFront MCP server")

    # Categorize URLs by datasource type (do this once)
    api_urls = [url for url in clean_urls if get_datasource_type(url) == DatasourceType.API]
    library_urls = [url for url in clean_urls if get_datasource_type(url) == DatasourceType.LIBRARY]
    database_urls = [url for url in clean_urls if get_datasource_type(url) == DatasourceType.DATABASE]

    async def discover() -> dict[str, list[str]]:
        """
        Lists all available datasources.

        Discover Instructions:
        1. Use this tool to list all available datasources.
        2. Passwords and secrets are obfuscated in the URL for security, but you can use the URLs as-is in other tools.
        """

        result = {}

        # Only include keys that have data
        if database_urls:
            result["databases"] = database_urls
        if library_urls:
            result["document_libraries"] = library_urls
        if api_urls:
            result["apis"] = api_urls

        return result

    # Always include discover tool
    mcp.add_tool(discover)

    # Check for different URL patterns using pre-categorized lists
    has_api_urls = bool(api_urls)
    has_library_urls = bool(library_urls)
    has_db_urls = bool(database_urls)

    # Add API tools if we have API URLs
    if has_api_urls:
        from toolfront.tools.api import inspect_endpoint, request_api, search_endpoints

        mcp.add_tool(inspect_endpoint)
        mcp.add_tool(request_api)

        # Add search_endpoints if we have API URLs
        mcp.add_tool(search_endpoints)

    # Add library tools if we have library URLs
    if has_library_urls:
        from toolfront.tools.library import read_document, search_documents

        mcp.add_tool(search_documents)
        mcp.add_tool(read_document)

    # Add database tools if we have database URLs
    if has_db_urls:
        from toolfront.tools.database import inspect_table, query_database, sample_table, search_queries, search_tables

        mcp.add_tool(inspect_table)
        mcp.add_tool(query_database)
        mcp.add_tool(sample_table)
        mcp.add_tool(search_tables)

        # Add search_queries if we have both database URLs and API key
        if api_key:
            mcp.add_tool(search_queries)

    return mcp


@click.command()
@click.option("--api-key", envvar="KRUSKAL_API_KEY", help="API key for authentication")
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="stdio", help="Transport mode for MCP server")
@click.argument("urls", nargs=-1)
def main(api_key: str | None = None, transport: Literal["stdio", "sse"] = "stdio", urls: tuple[str, ...] = ()) -> None:
    logger.info("Starting MCP server")
    mcp_instance = asyncio.run(get_mcp(urls, api_key))
    mcp_instance.run(transport=transport)


if __name__ == "__main__":
    main()
