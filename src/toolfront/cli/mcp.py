import click
from mcp.server.fastmcp import FastMCP

from toolfront.application import Application


@click.command()
@click.argument("url", type=click.STRING, required=True)
@click.option(
    "--param",
    "-p",
    multiple=True,
    default=None,
    help="Authentication parameter for the remote application: KEY=VALUE",
)
@click.option("--host", type=click.STRING, default="127.0.0.1", help="Host to run the server on")
@click.option("--port", type=click.INT, default=8000, help="Port to run the server on")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "streamable-http", "sse"]),
    default="stdio",
    help="Transport mode for MCP server",
)
@click.option("--env", type=click.STRING, default=None, help="Application variables to pass to the server")
def mcp(url, param, host, port, transport, env) -> None:
    """Start an MCP server for interacting with applications.

    Parameters
    ----------
    url : str
        Application directory path
    param : tuple[str, ...]
        Authentication parameters for remote application (KEY=VALUE, can be repeated)
    host : str
        Server host address (default: 127.0.0.1)
    port : int
        Server port number (default: 8000)
    transport : str
        MCP transport mode: stdio, streamable-http, or sse (default: stdio)
    env : str
        Application variables to pass to the server (KEY=VALUE)
    """
    if transport == "stdio":
        click.echo("Starting MCP server", err=True)
    else:
        click.echo("Starting MCP server")

    application = Application(url=url, param=param, env=env)

    mcp = FastMCP("ToolFront MCP server", host=host, port=port)

    mcp.add_tool(application.action)

    if transport == "stdio":
        click.echo("MCP server started successfully", err=True)
    else:
        click.echo("MCP server started successfully")
    mcp.run(transport=transport)
