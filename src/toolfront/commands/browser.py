import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

import click
from mcp.server.fastmcp import Context, FastMCP

from toolfront.browser import ToolPage


class JSONType(click.ParamType):
    """Custom Click parameter type for JSON parsing.

    Attributes
    ----------
    name : str
        Parameter type name for error messages
    """
    name = "json"

    def convert(self, value, param, ctx):
        """Convert string value to JSON object.

        Parameters
        ----------
        value : str
            String representation of JSON
        param : click.Parameter
            Click parameter context
        ctx : click.Context
            Click command context

        Returns
        -------
        Any
            Parsed JSON object

        Raises
        ------
        click.BadParameter
            If JSON parsing fails
        """
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            self.fail(f"Invalid JSON: {e}", param, ctx)


JSON = JSONType()


@dataclass
class AppContext:
    """Application context with typed dependencies.

    Attributes
    ----------
    page : ToolPage
        Current page being served by the MCP server
    """

    page: ToolPage


@click.group()
def browser():
    """Browser commands for MCP server functionality."""
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
    """Start an MCP server with a browsing environment.

    Usage: `browser serve URL [OPTIONS]`

    Parameters
    ----------
    url : str
        Starting URL or file path for the environment
    params : tuple[str, ...]
        Authentication parameters for the filesystem protocol: KEY=VALUE
    host : str
        Host to run the server on
    port : int
        Port to run the server on
    transport : str
        Transport mode for MCP server

    Example
    -------
    Start the browser MCP server with stdio transport pointing to a local directory:
    ```bash
    uvx toolfront browser serve file:///path/to/mysite --transport stdio
    ```


    Example
    -------
    Start the browser MCP server with streamable-http transport pointing to a S3 bucket:
    ```bash
    uvx toolfront browser serve s3:///path/to/mysite --transport streamable-http --params AWS_ACCESS_KEY_ID=1234567890 --params AWS_SECRET_ACCESS_KEY=1234567890
    ```

    Example
    -------
    Start the browser MCP server with sse transport pointing to a git repository:
    ```bash
    uvx toolfront browser serve git://path/to/mysite --transport sse --params GIT_TOKEN=1234567890
    ```
    """
    click.echo("Starting MCP server")

    params = dict([param.split("=") for param in params])

    page = ToolPage(url=url, params=params, env=None)

    @asynccontextmanager
    async def lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
        """Manage application lifecycle with type-safe context.

        Parameters
        ----------
        server : FastMCP
            MCP server instance

        Yields
        ------
        AppContext
            Application context with current page
        """
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

        Parameters
        ----------
        url : str
            Target URL or file path to navigate to
        ctx : Any
            MCP server context

        Returns
        -------
        str
            Page content with available commands
        """
        page = ToolPage(url=url, params=params, env=None)
        ctx.request_context.lifespan_context.page = page
        return await page.body()

    async def run_command(command: list[str], ctx: Context):
        """Run a command.

        Run CLI commands in a subprocess and return their output.

        ALWAYS UNDERSTAND THE ARGUMENTS AND OPTIONS BEFORE RUNNING COMMAND.

        Parameters
        ----------
        command : list[str]
            Command parts (executable and arguments)
        ctx : Any
            MCP server context

        Returns
        -------
        str
            Command output or error message
        """
        page = ctx.request_context.lifespan_context.page
        return await page.run_command(command, help_fallback=False)

    mcp.add_tool(navigate)
    mcp.add_tool(run_command)

    click.echo("MCP server started successfully")
    mcp.run(transport=transport)
