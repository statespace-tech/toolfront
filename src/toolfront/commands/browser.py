import click
from mcp.server.fastmcp import FastMCP

from toolfront.environment import Environment


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
@click.option("--env", type=click.STRING, default=None, help="Environment variables to pass to the server")
def serve(url, params, host, port, transport, env) -> None:
    """Start an MCP server for browsing environments.

    ToolFront's Model Context Protocol (MCP) server exposes environment browsing tools for use with custom AI agents. The server provides tools for reading files, running commands, and searching content.

    Usage: `toolfront browser serve URL [OPTIONS]`

    Parameters
    ----------
    url : str
        Environment URL or file path (file://, https://, s3://, etc.)
    params : tuple[str, ...]
        Authentication parameters for filesystem protocols: KEY=VALUE (can be used multiple times)
    host : str
        Server host address (default: 127.0.0.1)
    port : int
        Server port number (default: 8000)
    transport : str
        MCP transport mode: stdio, streamable-http, or sse (default: stdio)
    env : str
        Environment variables to pass to the server: KEY=VALUE

    Example
    -------
    Start with stdio transport for local environments:

    ```bash
    toolfront browser serve file:///path/to/mysite
    ```

    Example
    -------
    Start with HTTP transport for remote access:

    ```bash
    toolfront browser serve file:///path/to/mysite --transport streamable-http --port 8080
    ```

    Example
    -------
    Connect to S3 with authentication:

    ```bash
    toolfront browser serve s3://bucket/mysite --params AWS_ACCESS_KEY_ID=xxx --params AWS_SECRET_ACCESS_KEY=yyy
    ```

    Example
    -------
    Connect to GitHub repository:

    ```bash
    toolfront browser serve github://org/repo/mysite --params GH_TOKEN=xxx
    ```
    """
    click.echo("Starting MCP server")

    environment = Environment(url=url, params=params, env=env)

    mcp = FastMCP("ToolFront MCP server", host=host, port=port)

    mcp.add_tool(environment.run_command)
    mcp.add_tool(environment.read)
    mcp.add_tool(environment.glob)

    # Only add search tool if index page exists
    if environment.index_page:
        mcp.add_tool(environment.search)

    click.echo("MCP server started successfully")
    mcp.run(transport=transport)
