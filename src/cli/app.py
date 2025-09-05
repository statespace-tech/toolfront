import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

app = FastAPI()


@app.get("/{full_path:path}")
async def serve_file(full_path: str):
    """
    Serve files from CONTENT_DIR.
    If path ends in / or file not found, serve index.md.
    Markdown files are rendered to HTML, SQL and others are plain text.
    """
    # Resolve requested path in content dir
    abs_path = Path(os.environ["CONTENT_DIR"]) / full_path

    # If it's a directory or doesn't exist, try index.md
    if abs_path.is_dir() or not abs_path.exists():
        abs_path = abs_path / "index.md"

    # Check file exists
    if not abs_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {full_path}")

    # Serve Markdown as HTML
    if abs_path.endswith(".md"):
        md_content = abs_path.read_text(encoding="utf-8")
        return PlainTextResponse(content=md_content)

    # Serve SQL or other files as plain text
    content = abs_path.read_text(encoding="utf-8")
    return PlainTextResponse(content=content)
