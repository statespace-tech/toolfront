import click
from mcp.server.fastmcp import FastMCP

from toolfront.environment import Environment


@click.group()
def mcp():
    """ToolFront CLI"""
    pass


@mcp.command()
@click.argument("url", type=click.STRING, required=True)
@click.option(
    "--param",
    "-p",
    multiple=True,
    default=None,
    help="Authentication parameter for the remote environment: KEY=VALUE",
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
def serve(url, param, host, port, transport, env) -> None:
    """Start an MCP server for interacting with environments.

    Parameters
    ----------
    url : str
        Environment URL or file path (file://, https://, s3://, etc.)
    param : tuple[str, ...]
        Authentication parameters for remote environment (KEY=VALUE, can be repeated)
    host : str
        Server host address (default: 127.0.0.1)
    port : int
        Server port number (default: 8000)
    transport : str
        MCP transport mode: stdio, streamable-http, or sse (default: stdio)
    env : str
        Environment variables to pass to the server (KEY=VALUE)
    """
    click.echo("Starting MCP server")

    environment = Environment(url=url, param=param, env=env)

    mcp = FastMCP("ToolFront MCP server", host=host, port=port)

    mcp.add_tool(environment.execute)
    mcp.add_tool(environment.read)
    mcp.add_tool(environment.tree)
    mcp.add_tool(environment.glob)
    mcp.add_tool(environment.grep)

    click.echo("MCP server started successfully")
    mcp.run(transport=transport)


if __name__ == "__main__":
    mcp()
