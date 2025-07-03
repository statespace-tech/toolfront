import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Literal

import click
import httpx
from mcp.server.fastmcp import FastMCP

from toolfront.config import API_KEY_HEADER, BACKEND_URL
from toolfront.storage import save_connection
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

logger = logging.getLogger("toolfront")
logger.setLevel(logging.INFO)

logging.info("Starting ToolFront MCP server")


@dataclass
class AppContext:
    datasources: list[str]
    http_session: httpx.AsyncClient | None = None


async def get_mcp(urls: tuple[str, ...], api_key: str | None = None) -> FastMCP:
    cleaned_urls = [url.lstrip("'").rstrip("'") for url in urls]

    # Process all datasources concurrently
    datasources = await asyncio.gather(*[save_connection(url) for url in cleaned_urls])

    @asynccontextmanager
    async def app_lifespan(mcp_server: FastMCP) -> AsyncIterator[AppContext]:
        """Manage application lifecycle with type-safe context"""
        if api_key:
            headers = {API_KEY_HEADER: api_key}
            async with httpx.AsyncClient(headers=headers, base_url=BACKEND_URL) as http_client:
                yield AppContext(datasources=datasources, http_session=http_client)
        else:
            yield AppContext(datasources=datasources)

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
    logger.info("Starting MCP server with urls: \n\t%s", "\n\t".join(urls))
    mcp_instance = asyncio.run(get_mcp(urls, api_key))
    mcp_instance.run(transport=transport)


if __name__ == "__main__":
    main()
