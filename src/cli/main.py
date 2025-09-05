import asyncio
import logging
import os
from pathlib import Path
from typing import Literal

import click
import sqlglot
import uvicorn
import yaml
from mcp.server.fastmcp import FastMCP

from toolfront.models.base import DataSource

logger = logging.getLogger("toolsite")
logger.setLevel(logging.INFO)
logging.getLogger("sqlglot").setLevel(logging.ERROR)


async def get_mcp(url: str) -> FastMCP:
    datasource = DataSource.from_url(url)

    async def context() -> dict:
        """
        ALWAYS CALL THIS FIRST TO RETRIEVE THE CONTEXT FOR THE TASK.
        THEN, FOLLOW THE INSTRUCTIONS IN THE CONTEXT TO COMPLETE THE TASK.
        """
        return datasource.context()

    mcp = FastMCP("ToolFront MCP server")

    mcp.add_tool(context)

    for tool in datasource.tools():
        mcp.add_tool(tool, description=tool.__doc__)

    logger.info("Started ToolFront MCP server")

    return mcp


@click.group()
def cli():
    """Toolsite CLI"""
    pass


@cli.command()
@click.option("--host", "-h", default="0.0.0.0", help="Host to run the server on")
@click.option("--port", "-p", default=8000, help="Port to run the server on")
@click.option("--directory", "-d", default="./", help="Path to content directory")
@click.option(
    "--autoreload/--no-autoreload",
    "-r",
    default=False,
    help="Reload the server on code changes",
)
def serve(host, port, directory, autoreload):
    """Start the development server"""
    os.environ["CONTENT_DIR"] = directory
    uvicorn.run("cli.app:app", host=host, port=port, reload=autoreload)


@cli.command()
@click.option("--directory", "-d", default="./", help="Path to content directory")
def check(directory):
    """Build command (placeholder)"""
    issues = []

    for md_file in Path(directory).rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        try:
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    yaml.safe_load(parts[1])
        except Exception as e:
            issues.append(f"Error parsing markdown file {md_file} - {str(e)}")

    for sql_file in Path(directory).rglob("*.sql"):
        content = sql_file.read_text(encoding="utf-8")

        try:
            sqlglot.parse_one(content, dialect="duckdb")
        except Exception as e:
            issues.append(f"Error parsing SQL file {sql_file} - {str(e)}")

    if len(issues):
        logging.error(f"{len(issues)} issues found")
        for issue in issues:
            logging.error(issue)
        exit(1)
    logging.info("No issues found")


@cli.command()
@click.argument("url", type=click.STRING, required=True)
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="stdio", help="Transport mode for MCP server")
def mcp(url: str, transport: Literal["stdio", "sse"] = "stdio") -> None:
    logger.info("Starting MCP server")
    mcp_instance = asyncio.run(get_mcp(url))
    mcp_instance.run(transport=transport)


if __name__ == "__main__":
    cli()
