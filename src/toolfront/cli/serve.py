import asyncio
import contextlib
import re
import tomllib
from importlib.resources import files
from pathlib import Path
from typing import Any

import click
import uvicorn
import yaml
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

OPTIONS_DISABLED = ";"  # Marker to disable additional flags/arguments
TIMEOUT = 30


class ActionRequest(BaseModel):
    """Request model for executing commands via POST endpoint.

    Attributes:
        command: Command as list of strings (e.g., ["cat", "file.txt", "-n"])
        env: Optional environment variables to pass to the subprocess
    """

    command: list[str]
    env: dict[str, str] | None = None


def _parse_frontmatter(markdown: str) -> dict[str, Any]:
    """Parse YAML or TOML frontmatter from markdown content."""
    # Try YAML frontmatter (--- ... ---)
    yaml_pattern = r"^\n*---\s*\n(.*?)\n---\s*\n(.*)"
    if match := re.match(yaml_pattern, markdown, re.DOTALL):
        try:
            return yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            return {}

    # Try TOML frontmatter (+++ ... +++)
    toml_pattern = r"^\n*\+\+\+\s*\n(.*?)\n\+\+\+\s*\n(.*)"
    if match := re.match(toml_pattern, markdown, re.DOTALL):
        try:
            return tomllib.loads(match.group(1))
        except tomllib.TOMLDecodeError:
            return {}

    return {}


def _validate_command(base_command: list[str], tool_command: list[str], options_disabled: bool) -> bool:
    """Validate command against tool specification (base + options)."""

    # Check command length
    if len(tool_command) < len(base_command):
        return False

    # Validate base parts (with placeholder/regex support)
    for i, base_part in enumerate(base_command):
        if isinstance(base_part, dict):
            if "regex" in base_part and not bool(re.match(base_part["regex"], tool_command[i])):
                return False
        elif tool_command[i] != base_part:
            return False

    # Validate additional arguments
    extra_parts = tool_command[len(base_command) :]
    if not extra_parts:
        return True

    # If options disabled, reject any extra arguments
    return not options_disabled


def _is_valid_tool_call(tool_command: list[str], tools: list) -> bool:
    """Validate tool call against tool specifications."""
    for tool in tools:
        # Validate tool call against tool specification
        if isinstance(tool, list):
            options_disabled = tool[-1] == OPTIONS_DISABLED if tool else False
            base_command = tool[:-1] if options_disabled else tool
            if _validate_command(base_command, tool_command, options_disabled):
                return True
    return False


def _resolve_file_path(directory: Path, file_path: str) -> Path:
    """Resolve and validate file path (security checks + .md/.README.md resolution).

    Resolution order:
    1. If path exists as-is and is a file, serve it
    2. If path is a directory, serve directory/README.md
    3. If path doesn't exist, try adding .md extension
    4. Otherwise, 404
    """
    # Normalize: strip leading/trailing slashes, handle empty path
    file_path = file_path.strip("/") or "."

    # Resolve to absolute path
    full_path = (directory / file_path).resolve()

    # Security: prevent directory traversal
    if not full_path.is_relative_to(directory):
        raise HTTPException(status_code=403, detail="Access denied: path outside served directory")

    # Case 1: Path exists as-is and is a file
    if full_path.is_file():
        return full_path

    # Case 2: Path is a directory, serve README.md
    if full_path.is_dir():
        readme_path = full_path / "README.md"
        if readme_path.is_file():
            return readme_path
        raise HTTPException(status_code=404, detail=f"Directory found but no README.md: {file_path}")

    # Case 3: Path doesn't exist, try adding .md extension
    if not str(full_path).endswith(".md"):
        md_path = Path(str(full_path) + ".md")
        if md_path.is_file():
            return md_path

    # Case 4: Not found
    raise HTTPException(status_code=404, detail=f"File not found: {file_path}")


@click.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--host", default="127.0.0.1", help="Host to bind the server to")
@click.option("--port", default=8000, type=int, help="Port to bind the server to")
def serve(directory: str, host: str, port: int) -> None:
    """Serve a ToolFront application directory via HTTP.

    Exposes two endpoints:
    - GET /{file_path} - Read markdown files
    - POST /{file_path} - Execute commands defined in frontmatter

    Args:
        directory: Path to the application directory (must contain README.md)
        host: Host address to bind the server to
        port: Port number to bind the server to
    """
    directory_path = Path(directory).resolve()

    # Validate directory has README.md
    if not (directory_path / "README.md").exists():
        click.echo("Error: README.md not found in directory", err=True)
        raise click.Abort()

    # Copy template files if they don't exist
    templates = files("toolfront") / "templates"

    if not (directory_path / "robots.txt").exists():
        robots_txt_content = (templates / "robots.txt").read_text()
        (directory_path / "robots.txt").write_text(robots_txt_content)

    if not (directory_path / "favicon.svg").exists():
        favicon_content = (templates / "favicon.svg").read_text()
        (directory_path / "favicon.svg").write_text(favicon_content)

    if not (directory_path / "index.html").exists():
        index_html_content = (templates / "index.html").read_text()
        # Replace placeholders
        current_url = f"http://{host}:{port}"
        robots_txt_content = (directory_path / "robots.txt").read_text()
        index_html_content = index_html_content.replace("{current_url}", current_url).replace(
            "{robots_txt_content}", robots_txt_content
        )
        (directory_path / "index.html").write_text(index_html_content)

    app = FastAPI(title="ToolFront Application")

    @app.get("/favicon.svg")
    async def get_favicon():
        """Serve the favicon from the directory."""
        favicon_path = directory_path / "favicon.svg"
        if favicon_path.exists():
            return FileResponse(favicon_path, media_type="image/svg+xml")
        raise HTTPException(status_code=404, detail="Favicon not found")

    @app.get("/{file_path:path}")
    async def read_file(file_path: str):
        """Read a markdown file from the served directory."""
        # Serve index.html for root path
        if not file_path.strip("/"):
            index_path = directory_path / "index.html"
            if index_path.exists():
                return FileResponse(index_path, media_type="text/html")

        # Default behavior for all other paths
        resolved_path = _resolve_file_path(directory_path, file_path)
        return FileResponse(resolved_path)

    @app.post("/{file_path:path}")
    async def execute_action(file_path: str, action: ActionRequest = Body(...)) -> JSONResponse:
        """Execute a command defined in a file's frontmatter."""

        # Validate command
        if not action.command:
            raise HTTPException(status_code=400, detail="Empty command")

        # Resolve and parse file
        resolved_path = _resolve_file_path(directory_path, file_path)
        frontmatter = _parse_frontmatter(resolved_path.read_text())

        if not frontmatter:
            raise HTTPException(status_code=400, detail=f"No frontmatter found in: {resolved_path.name}")

        tools = frontmatter.get("tools", [])
        if not tools:
            raise HTTPException(status_code=400, detail=f"No tools defined in frontmatter of: {resolved_path.name}")

        if not _is_valid_tool_call(action.command, tools):
            raise HTTPException(status_code=403, detail=f"Command not allowed: {action.command}")

        try:
            process = await asyncio.create_subprocess_exec(
                *action.command,
                cwd=resolved_path.parent,
                env=action.env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=TIMEOUT)
            except TimeoutError:
                with contextlib.suppress(ProcessLookupError):
                    process.kill()
                raise HTTPException(status_code=408, detail="Command execution timeout")

            return JSONResponse(
                content={
                    "stdout": stdout.decode() if stdout else "",
                    "stderr": stderr.decode() if stderr else "",
                    "returncode": process.returncode,
                }
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Command execution failed: {str(e)}") from e

    # Start server
    click.echo(f"Starting ToolFront server on {host}:{port} from {directory_path}")
    uvicorn.run(app, host=host, port=port, log_level="info")
