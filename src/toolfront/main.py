import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Literal
from urllib.parse import parse_qs, urlparse

import click
import diskcache
import httpx
import jsonref
from mcp.server.fastmcp import FastMCP

from toolfront.config import API_KEY_HEADER, BACKEND_URL
from toolfront.models.connection import Connection
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

logger = logging.getLogger("toolfront")
logger.setLevel(logging.INFO)

_cache = diskcache.Cache(".toolfront_cache")


def get_openapi_spec(url: str) -> dict | None:
    """Get OpenAPI spec with retries if cached result is None."""
    cache_key = url

    # Check if we have a cached result
    if cache_key in _cache:
        cached_result = _cache[cache_key]
        if cached_result is not None:
            logger.debug(f"Cache hit for {url}")
            return cached_result
        else:
            # Remove None from cache and retry
            logger.debug(f"Cached None for {url}, removing and retrying")
            del _cache[cache_key]

    # Download and cache if successful
    try:
        logger.debug(f"Downloading OpenAPI spec for {url}")
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
            spec = response.json()

            parsed_spec = jsonref.replace_refs(spec)
            # Only cache non-None results
            _cache.set(cache_key, parsed_spec, expire=3600)  # 1 hour TTL
            logger.info(f"Successfully retrieved spec for {url}")
            return parsed_spec
    except Exception as e:
        logger.warning(f"Failed to retrieve spec from {url}: {e}")
        return None


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

        servers = spec.get("servers", []) if spec else []
        url = servers[0].get("url", None) if servers else None

        # If no API URL is provided, use the parsed URL
        if url is None:
            url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            # If the API URL is a relative path, prepend the parsed URL
            if url.startswith("/"):
                url = f"https://{parsed.netloc}{url}"

        # Parse query parameters into a dictionary
        query_params = parse_qs(parsed.query)
        # Convert from lists to single values
        query_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}

        # Handle authentication based on OpenAPI spec
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

        extra = {
            "openapi_spec": spec,
            "query_params": query_params,
            "auth_headers": auth_headers,
            "auth_query_params": auth_query_params,
        }

    # Create structured URL objects
    if parsed.scheme in ("http", "https"):
        # Create API URL with auth info
        url_obj = APIURL.from_url_string(
            url, auth_headers=auth_headers, auth_query_params=auth_query_params, query_params=query_params
        )
    else:
        # Create database URL
        url_obj = DatabaseURL.from_url_string(url)

    # Store metadata with the URL object
    metadata = {"parsed": parsed, "extra": extra}

    try:
        logger.info("Creating connection from URL (password automatically hidden)")
        # Create connection using the structured URL object
        if parsed.scheme in ("http", "https"):
            connection = Connection.from_url(
                url, auth_headers=auth_headers, auth_query_params=auth_query_params, query_params=query_params
            )
        else:
            # Use the structured URL object directly for database connections
            from toolfront.models.connection import DatabaseConnection

            connection = DatabaseConnection(url=url_obj)
        logger.info(f"Connection type: {type(connection)}")

        logger.info("Testing connection")
        # Test connection
        result = await connection.test_connection(url_map={})

        if result.connected:
            logger.warning("Connection successful")
        else:
            logger.warning(f"Connection failed: {result.message}")
    except Exception as e:
        logger.error(f"Exception during connection process: {type(e).__name__}: {e}")
        import traceback

        logger.error(f"Full traceback: {traceback.format_exc()}")
        from toolfront.models.database import ConnectionResult

        result = ConnectionResult(connected=False, message=f"Connection error: {e}")

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
