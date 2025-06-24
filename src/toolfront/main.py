import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Literal

import click
import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from sqlalchemy.engine.url import make_url

from toolfront.config import API_KEY_HEADER, BACKEND_URL
from toolfront.models.connection import Connection
from toolfront.tools import discover, inspect, query, sample, search_queries, search_tables, test

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("toolfront")


@dataclass
class AppContext:
    http_session: httpx.AsyncClient | None = None
    url_map: dict = Field(default_factory=dict)


async def test_connections(urls: tuple[str, ...]) -> None:
    """Test all connections in parallel"""
    if not urls:
        return

    async def _test_connection(url: str) -> None:
        """Test database connection"""
        connection = Connection(url=url)
        result = await connection.test_connection()
        if not result.connected:
            raise RuntimeError(f"Failed to connect to {url}: {result.message}")
        logger.info(f"Connection successful to {url}")

    await asyncio.gather(*(_test_connection(url) for url in urls))


def get_mcp(urls: tuple[str, ...], api_key: str | None = None) -> FastMCP:
    cleaned_urls = [url.lstrip("'").rstrip("'") for url in urls]

    # Test all connections asynchronously before starting the MCP server
    url_map = {str(url_obj): url_obj for url_obj in map(make_url, cleaned_urls)}

    asyncio.run(test_connections(cleaned_urls))

    @asynccontextmanager
    async def app_lifespan(mcp_server: FastMCP) -> AsyncIterator[AppContext]:
        """Manage application lifecycle with type-safe context"""
        if api_key:
            headers = {API_KEY_HEADER: api_key}
            async with httpx.AsyncClient(headers=headers, base_url=BACKEND_URL) as http_client:
                yield AppContext(http_session=http_client, url_map=url_map)
        else:
            yield AppContext(url_map=url_map)

    mcp = FastMCP("ToolFront MCP server", lifespan=app_lifespan)

    mcp.add_tool(discover)
    mcp.add_tool(inspect)
    mcp.add_tool(sample)
    mcp.add_tool(query)
    mcp.add_tool(search_tables)
    mcp.add_tool(test)

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
    mcp_instance = get_mcp(urls, api_key)
    mcp_instance.run(transport=transport)


if __name__ == "__main__":
    main()
