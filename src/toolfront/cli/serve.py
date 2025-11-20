import re
import subprocess
import tomllib
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


def _resolve_file_path(directory: Path, file_path: str) -> str:
    """Resolve and validate file path (security checks + .md/.README.md resolution)."""
    full_path = (directory / file_path).resolve()

    # Security: prevent directory traversal
    if not full_path.is_relative_to(directory):
        raise HTTPException(status_code=403, detail="Access denied: path outside served directory")

    # Direct .md file
    if file_path.endswith(".md"):
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        if not full_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        return str(full_path)

    # Try README.md in directory
    readme_path = full_path / "README.md"
    if readme_path.exists() and readme_path.is_file():
        return str(readme_path)

    raise HTTPException(status_code=404, detail="File not found (tried README.md)")


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

    app = FastAPI(title="ToolFront Application")

    @app.get("/{file_path:path}")
    async def read_file(file_path: str) -> FileResponse:
        """Read a markdown file from the served directory."""
        full_path = _resolve_file_path(directory_path, file_path)
        return FileResponse(full_path)

    @app.post("/{file_path:path}")
    async def execute_action(file_path: str, action: ActionRequest = Body(...)) -> JSONResponse:
        """Execute a command defined in a file's frontmatter."""

        # Validate command
        if not action.command:
            raise HTTPException(status_code=400, detail="Empty command")

        # Resolve and parse file
        full_path = _resolve_file_path(directory_path, file_path)
        path = Path(full_path)
        frontmatter = _parse_frontmatter(path.read_text())

        if not frontmatter:
            raise HTTPException(status_code=400, detail=f"No frontmatter found in: {path.name}")

        tools = frontmatter.get("tools", [])
        if not tools:
            raise HTTPException(status_code=400, detail=f"No tools defined in frontmatter of: {path.name}")

        if not _is_valid_tool_call(action.command, tools):
            raise HTTPException(status_code=403, detail=f"Command not allowed: {action.command}")

        try:
            result = subprocess.run(action.command, cwd=path.parent, env=action.env, capture_output=True, text=True, timeout=TIMEOUT)
            return JSONResponse(content={"stdout": result.stdout or "", "stderr": result.stderr or "", "returncode": result.returncode})
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=408, detail="Command execution timeout")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Command execution failed: {str(e)}") from e

    # Start server
    click.echo(f"Starting ToolFront server on {host}:{port} from {directory_path}")
    uvicorn.run(app, host=host, port=port, log_level="info")
