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

    # CRITICAL: Pre-bind the application URL to prevent LLM confusion
    #
    # Problem: The LLM was extracting URLs from command arguments (e.g., from curl commands)
    # and using them as the 'url' parameter for the action() tool, causing POSTs to go to
    # the wrong endpoint (405 errors) pretty consistently.
    #
    # Root cause: When the LLM sees action(url, command, args) as a tool signature, and then
    # encounters a command like ["curl", "-X", "GET", "https://api.toolfront.ai/health"], it
    # incorrectly assumes the URL in the command is what should be passed to the 'url' parameter.
    #
    # Incorrect flow (before this fix):
    #   1. LLM sees: action(url, command, args)
    #   2. LLM reads command: ["curl", "-X", "GET", "https://api.toolfront.ai/health"]
    #   3. LLM calls: action(url="https://api.toolfront.ai/health", command=[...])
    #   4. POST goes to https://api.toolfront.ai/health instead of the markdown file URL
    #   5. Server returns 405 Method Not Allowed (GET endpoint, not POST)
    #
    # Corrected flow (with this wrapper):
    #   1. LLM sees: action_wrapper(command, args) - url parameter is hidden
    #   2. LLM reads command: ["curl", "-X", "GET", "https://api.toolfront.ai/health"]
    #   3. LLM calls: action_wrapper(command=["curl", ...], args=None)
    #   4. Wrapper automatically injects: url=str(application.url)
    #   5. POST goes to correct markdown file URL (e.g., https://env-abc123.toolfront.ai/README.md)
    #   6. Environment server validates command is in frontmatter, executes it, returns result
    #
    # By hiding the 'url' parameter from the LLM's view, we prevent it from making incorrect
    # assumptions about which URL to use. The application URL is always the markdown file where
    # the tool is defined, never a URL that happens to appear in the command arguments.
    async def action_wrapper(command: list[str], args: dict[str, str] | None = None) -> str:
        return await application.action(url=str(application.url), command=command, args=args)

    mcp.add_tool(action_wrapper)

    if transport == "stdio":
        click.echo("MCP server started successfully", err=True)
    else:
        click.echo("MCP server started successfully")
    mcp.run(transport=transport)
