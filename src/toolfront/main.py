import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlparse

import click
import httpx
from mcp.server.fastmcp import FastMCP

from toolfront.config import API_KEY_HEADER, BACKEND_URL
from toolfront.models.connection import APIConnection, DatabaseConnection
from toolfront.models.url import APIURL, DatabaseURL
from toolfront.tools import (
    discover,
    inspect_endpoint,
    inspect_table,
    query_database,
    request_api,
    sample_table,
    search_endpoints,
    search_queries,
    search_tables,
)
from toolfront.utils import get_openapi_spec, parse_api_url

logger = logging.getLogger("toolfront")
logger.setLevel(logging.INFO)

logging.info("Starting ToolFront MCP server")


@dataclass
class AppContext:
    http_session: httpx.AsyncClient | None = None
    url_objects: list = None  # Store original URL objects directly
    metadata_map: dict = None  # Store metadata by URL string

    def __post_init__(self):
        if self.url_objects is None:
            self.url_objects = []
        if self.metadata_map is None:
            self.metadata_map = {}


async def process_datasource(url: str) -> tuple:
    """Process datasource: parse, download spec, test connection

    Returns:
        tuple: (url_object, metadata)
    """

    parsed = urlparse(url)
    extra = {}

    if parsed.scheme in ("http", "https"):
        spec = get_openapi_spec(url)
        parse_result = parse_api_url(url, spec)
        url = parse_result.url
        extra = {
            "openapi_spec": parse_result.openapi_spec,
            "query_params": parse_result.query_params,
            "auth_headers": parse_result.auth_headers,
            "auth_query_params": parse_result.auth_query_params,
        }

    # Store metadata with the URL object
    metadata = {"parsed": parsed, "extra": extra}

    try:
        # Create connection using the structured URL object
        if parsed.scheme in ("http", "https"):
            url_obj = APIURL.from_url_string(url)
            connection = APIConnection(url=url_obj)
            result = await connection.test_connection(openapi_spec=spec)
        else:
            url_obj = DatabaseURL.from_url_string(url)
            connection = DatabaseConnection(url=url_obj)
            result = await connection.test_connection()

        logger.info(f"Connected to {url} - {result.connected}")

    except Exception as e:
        logging.error(f"Exception during connection process: {type(e).__name__}: {e}")
        import traceback

        logging.error(f"Full traceback: {traceback.format_exc()}")

    return url_obj, metadata


async def get_mcp(urls: tuple[str, ...], api_key: str | None = None) -> FastMCP:
    cleaned_urls = [url.lstrip("'").rstrip("'") for url in urls]

    # Process all datasources concurrently
    datasource_results = await asyncio.gather(*[process_datasource(url) for url in cleaned_urls])

    # Collect URL objects and metadata
    url_objects = [url_obj for url_obj, metadata in datasource_results]
    metadata_map = {str(url_obj): metadata for url_obj, metadata in datasource_results}

    @asynccontextmanager
    async def app_lifespan(mcp_server: FastMCP) -> AsyncIterator[AppContext]:
        """Manage application lifecycle with type-safe context"""
        if api_key:
            headers = {API_KEY_HEADER: api_key}
            async with httpx.AsyncClient(headers=headers, base_url=BACKEND_URL) as http_client:
                yield AppContext(http_session=http_client, url_objects=url_objects, metadata_map=metadata_map)
        else:
            yield AppContext(url_objects=url_objects, metadata_map=metadata_map)

    mcp = FastMCP("ToolFront MCP server", lifespan=app_lifespan)

    mcp.add_tool(discover)
    mcp.add_tool(inspect_endpoint)
    mcp.add_tool(inspect_table)
    mcp.add_tool(query_database)
    mcp.add_tool(request_api)
    mcp.add_tool(sample_table)
    mcp.add_tool(search_endpoints)
    mcp.add_tool(search_tables)

    if api_key:
        mcp.add_tool(search_queries)

    return mcp


@click.command()
@click.option("--api-key", envvar="KRUSKAL_API_KEY", help="API key for authentication")
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="stdio", help="Transport mode for MCP server")
@click.argument("urls", nargs=-1)
def main(api_key: str | None = None, transport: Literal["stdio", "sse"] = "stdio", urls: tuple[str, ...] = ()) -> None:
    """ToolFront CLI - Run the MCP server"""
    logger.info("Starting MCP server with urls: %s", urls)
    mcp_instance = asyncio.run(get_mcp(urls, api_key))
    mcp_instance.run(transport=transport)


if __name__ == "__main__":
    main()
