import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

import click
from mcp.server.fastmcp import Context, FastMCP

from toolfront.browser import ToolPage


class JSONType(click.ParamType):
    name = "json"

    def convert(self, value, param, ctx):
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            self.fail(f"Invalid JSON: {e}", param, ctx)


JSON = JSONType()


@dataclass
class AppContext:
    """Application context with typed dependencies."""

    page: ToolPage


@click.group()
def browser():
    """Browser commands"""
    pass


@browser.command()
@click.argument("url", type=click.STRING, required=True)
@click.option(
    "--params",
    "-p",
    multiple=True,
    default=None,
    help="Authentication parameters for the filesystem protocol: KEY=VALUE",
)
@click.option("--host", type=click.STRING, default="127.0.0.1", help="Host to run the server on")
@click.option("--port", type=click.INT, default=8000, help="Port to run the server on")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "streamable-http", "sse"]),
    default="stdio",
    help="Transport mode for MCP server",
)
def serve(url, params, host, port, transport) -> None:
    click.echo("Starting MCP server")

    params = dict([param.split("=") for param in params])

    page = ToolPage(url=url, params=params)

    @asynccontextmanager
    async def lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
        """Manage application lifecycle with type-safe context."""
        try:
            yield AppContext(page=page)
        finally:
            pass

    mcp = FastMCP(
        "ToolFront MCP server", lifespan=lifespan, host=host, port=port, instructions=asyncio.run(page.body())
    )

    async def navigate(url: str, ctx: Context):
        """Navigate to a page.

        Instructions:
        1. Only use only absolute file paths or URLs with protocol and domain
        2. When navigation fails check URI syntax and retry with corrected format.
        """
        page = ToolPage(url=url, params=params)
        ctx.request_context.lifespan_context.page = page
        return await page.body()

    async def run_command(command: list[str], ctx: Context):
        """Run a command.

        Run CLI commands in a subprocess and return their output.

        ALWAYS UNDERSTAND THE ARGUMENTS AND OPTIONS BEFORE RUNNING COMMAND.
        """
        page = ctx.request_context.lifespan_context.page
        return await page.run_command(command, help_fallback=False)

    mcp.add_tool(navigate)
    mcp.add_tool(run_command)

    click.echo("MCP server started successfully")
    mcp.run(transport=transport)
