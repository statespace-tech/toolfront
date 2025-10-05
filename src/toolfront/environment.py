import logging
import re
import subprocess
import tomllib
from enum import Enum
from typing import Any
from urllib.parse import parse_qsl, urlparse, urlunparse

import duckdb
import yaml
from fsspec import filesystem
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, field_validator, model_validator

from toolfront.utils import clean_url

logger = logging.getLogger("toolfront")

DEFAULT_HEAD_LIMIT = 20


def get_frontmatter(markdown: str) -> dict[str, Any]:
    """Parse frontmatter from markdown content and return dict (supports YAML and TOML).

    Args:
        markdown: Raw markdown content with optional frontmatter

    Returns:
        Tools as dict (empty dict if no tools)
    """
    # Try YAML frontmatter (--- ... ---)
    yaml_pattern = r"^\n*---\s*\n(.*?)\n---\s*\n(.*)"
    if match := re.match(yaml_pattern, markdown, re.DOTALL):
        try:
            return yaml.safe_load(match.group(1))
        except Exception as e:
            logger.warning(f"Failed to parse YAML frontmatter: {e}")
            return {}

    # Try TOML frontmatter (+++ ... +++)
    toml_pattern = r"^\n*\+\+\+\s*\n(.*?)\n\+\+\+\s*\n(.*)"
    if match := re.match(toml_pattern, markdown, re.DOTALL):
        try:
            return tomllib.loads(match.group(1))
        except Exception as e:
            logger.warning(f"Failed to parse TOML frontmatter: {e}")
            return {}

    return {}


class SearchType(str, Enum):
    """Search type for document searching."""

    BM25 = "bm25"
    REGEX = "regex"


class OutputMode(str, Enum):
    """Output modes for regex search."""

    CONTENT = "content"
    FILES_WITH_MATCHES = "files_with_matches"
    COUNT = "count"


class Stemmer(str, Enum):
    """Stemmer options for full-text search."""

    ARABIC = "arabic"
    BASQUE = "basque"
    CATALAN = "catalan"
    DANISH = "danish"
    DUTCH = "dutch"
    ENGLISH = "english"
    FINNISH = "finnish"
    FRENCH = "french"
    GERMAN = "german"
    GREEK = "greek"
    HINDI = "hindi"
    HUNGARIAN = "hungarian"
    INDONESIAN = "indonesian"
    IRISH = "irish"
    ITALIAN = "italian"
    LITHUANIAN = "lithuanian"
    NEPALI = "nepali"
    NORWEGIAN = "norwegian"
    PORTER = "porter"
    PORTUGUESE = "portuguese"
    ROMANIAN = "romanian"
    RUSSIAN = "russian"
    SERBIAN = "serbian"
    SPANISH = "spanish"
    SWEDISH = "swedish"
    TAMIL = "tamil"
    TURKISH = "turkish"
    NONE = "none"


class Stopwords(str, Enum):
    """Stopwords options for full-text search."""

    ENGLISH = "english"
    NONE = "none"


class CommandOutput(BaseModel):
    """Output of a command."""

    stdout: str = Field(..., description="Standard output of the command.")
    stderr: str = Field(..., description="Standard error of the command.")


class GlobOutput(BaseModel):
    """Output for glob mode."""

    matches: list[str] = Field(..., description="Array of matching file paths")
    count: int = Field(..., description="Number of matches")
    url_pattern: str = Field(..., description="URL pattern used")


class GrepMatch(BaseModel):
    """Output for grep mode."""

    file: str = Field(..., description="File path containing the match")
    line_number: int | None = Field(None, description="Line number of the match")
    line: str = Field(..., description="Matching line content")
    before_context: list[str] | None = Field(None, description="Lines before the match")
    after_context: list[str] | None = Field(None, description="Lines after the match")


class GrepContentOutput(BaseModel):
    """Output for content mode."""

    matches: list[GrepMatch] = Field(..., description="List of matches with content")
    total_matches: int = Field(..., description="Total number of matches found")


class GrepFilesOutput(BaseModel):
    """Output for files_with_matches mode."""

    files: list[str] = Field(..., description="Files containing matches")
    count: int = Field(..., description="Number of files with matches")


class GrepCountOutput(BaseModel):
    """Output for count mode."""

    total_matches: int = Field(..., description="Total number of matches across all files")


class ReadFileOutput(BaseModel):
    """Output for read file mode."""

    content: str = Field(..., description="File content with line numbers")
    total_lines: int = Field(..., description="Total number of lines in file")
    lines_returned: int = Field(..., description="Lines returned")


class BM25Result(BaseModel):
    """Single BM25 search result."""

    filename: str = Field(..., description="File path")
    score: float = Field(..., description="BM25 relevance score")


class BM25Output(BaseModel):
    """Output for BM25 search."""

    results: list[BM25Result] = Field(..., description="Search results ranked by BM25 score")
    total_results: int = Field(..., description="Total number of results found")
    query: str = Field(..., description="Search query used")
    url_pattern: str = Field(..., description="URL pattern searched")


class Environment(BaseModel):
    """Represents a environment with executable tools and content.

    Attributes
    ----------
    url : str
        Root URL for the environment - all operations must be within this URL
    params : dict[str, str] | None
        Authentication parameters for filesystem protocols
    env : dict[str, str] | None
        Environment variables for command execution
    home_page : str | None
        Home page URL for the environment (file if URL is a file, else index.md in directory)
    """

    url: str = Field(..., description="Root URL for the environment")
    params: dict[str, str] | None = Field(default=None, description="Query parameters for the page.", exclude=True)
    env: dict[str, str] | None = Field(default=None, description="Environment variables for the page.", exclude=True)
    home_page: str | None = Field(default=None, description="Home page for the environment")
    index_page: str | None = Field(default=None, description="Index page for the environment")

    _fs: Any = PrivateAttr(None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("params", mode="before")
    @classmethod
    def validate_params(cls, params: dict[str, str] | list[str] | tuple | None) -> dict[str, str] | None:
        """Convert list of KEY=VALUE strings to dict."""
        if isinstance(params, list | tuple):
            return dict(param.split("=", 1) for param in params)
        return params

    @field_validator("env", mode="before")
    @classmethod
    def validate_env(cls, env: dict[str, str] | list[str] | tuple | None) -> dict[str, str] | None:
        """Convert list of KEY=VALUE strings to dict."""
        if isinstance(env, list | tuple):
            return dict(env_var.split("=", 1) for env_var in env)
        return env

    @model_validator(mode="after")
    def validate_model(self) -> "Environment":
        """Initialize filesystem and determine home page."""
        url = clean_url(self.url)
        parsed = urlparse(url)

        # Setup filesystem
        kwargs = dict(parse_qsl(parsed.query, keep_blank_values=True))
        if isinstance(self.params, dict):
            kwargs.update(self.params)

        self._fs = filesystem(parsed.scheme, **kwargs)

        # Determine home page and normalize URL
        if self._fs.isfile(parsed.path):
            # URL points to a file - use it as home page, extract directory as root
            self.home_page = url
            parent_path = parsed.path.rsplit("/", 1)[0] if "/" in parsed.path else ""
            self.url = urlunparse((parsed.scheme, parsed.netloc, parent_path, "", "", ""))
        elif self._fs.isdir(parsed.path):
            # URL points to a directory - set root and try index.md as home
            self.url = url
            home_page = f"{parsed.path.rstrip('/')}/index.md"
            if self._fs.isfile(home_page):
                self.home_page = home_page
        else:
            raise ValueError(f"URL does not point to a valid file or directory: {url}")

        index_page = f"{parsed.path}/index.duckdb"
        if self._fs.isfile(index_page):
            self.index_page = index_page

        return self

    def _validate_url(self, url: str, require_type: str | None = None):
        """Validate URL is within environment root and return parsed URL.

        Parameters
        ----------
        url : str
            URL to validate (must be within environment root URL)
        require_type : str | None
            Required type: 'file', 'directory', or None for no validation

        Returns
        -------
        ParseResult
            Parsed and validated URL object

        Raises
        ------
        ValueError
            If URL doesn't match required type or is outside environment root
        FileNotFoundError
            If file is required but doesn't exist
        """
        url = clean_url(url)
        parsed = urlparse(url)
        root_parsed = urlparse(self.url)

        # Ensure URL is within the environment root
        if parsed.scheme != root_parsed.scheme:
            raise ValueError(f"URL scheme must match environment root: {url} (expected {root_parsed.scheme}://)")

        if parsed.netloc != root_parsed.netloc:
            raise ValueError(
                f"URL domain must match environment root: {url} (expected {root_parsed.scheme}://{root_parsed.netloc})"
            )

        # Normalize paths for comparison
        root_path = root_parsed.path.rstrip("/")
        url_path = parsed.path.rstrip("/")

        if not url_path.startswith(root_path):
            raise ValueError(f"URL must be within environment root: {url} (root: {self.url})")

        # Validate type if required
        if require_type == "file" and not self._fs.isfile(parsed.path):
            raise FileNotFoundError(f"File not found: {url}")
        elif require_type == "directory" and not self._fs.isdir(parsed.path):
            raise ValueError(f"URL must be a directory: {url}")

        return parsed

    async def run_command(self, command: list[str], page_url: str) -> CommandOutput:
        """Execute a command from a markdown page's frontmatter.

        Instructions:
        1. First read the markdown page to see available commands in its frontmatter
        2. Commands must exactly match those listed in the page's frontmatter
        3. If you don't know what a command does or what arguments it accepts, run it with --help flag first (e.g., ['command', '--help'])
        4. Use the help output to understand the command's usage before running it with actual arguments
        5. page_url MUST be an absolute file URL within the environment root (e.g., 'file:///path/to/page.md', 's3://bucket/path/page.md', 'https://example.com/docs/page.md')

        Parameters
        ----------
        command : list[str]
            Command and its arguments as a list (e.g., ['python', 'script.py', '--arg', 'value'])
        page_url : str
            Absolute file URL to the markdown (.md) page containing the command in its frontmatter

        Returns
        -------
        CommandOutput
            Object with stdout and stderr

        Raises
        ------
        RuntimeError
            If command is not listed in the page's frontmatter or execution fails
        """
        parsed = self._validate_url(page_url, require_type="file")

        # Validate it's a markdown file
        if not parsed.path.endswith(".md"):
            raise ValueError(f"page_url must point to a markdown (.md) file: {urlunparse(parsed)}")

        frontmatter = get_frontmatter(self._fs.read_text(parsed.path))
        if not frontmatter:
            raise RuntimeError(f"No frontmatter found in: {urlunparse(parsed)}")

        # Extract list of commands from frontmatter
        tools = frontmatter.get("tools", {})
        if not tools:
            raise RuntimeError(f"No tools found in frontmatter of: {urlunparse(parsed)}")

        # Validate tool matches one of the allowed tools
        if not any(command[: len(t)] == t for t in tools):
            raise RuntimeError(f"Invalid command: {command}. Must be one of: {tools}")

        # Execute command in the directory containing the markdown page (only for file:// URLs)
        cwd = None
        if parsed.scheme == "file":
            cwd = parsed.path.rsplit("/", 1)[0] if "/" in parsed.path else ""

        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)

        return CommandOutput(stdout=result.stdout, stderr=result.stderr)

    async def glob(self, path_url: str, pattern: str) -> GlobOutput:
        """Find files matching a glob pattern.

        Instructions:
        1. path_url MUST be an absolute directory URL within the environment root (e.g., 'file:///path/to/dir', 's3://bucket/path', 'https://example.com/files')
        2. All URLs must be within the environment's root URL
        3. pattern is the glob pattern to match (e.g., '**/*.py', '*.md', 'src/**/*.txt')
        4. Use ** for recursive directory matching
        5. Pattern is combined with the directory URL

        Examples:
        - Find Python files locally: path_url='file:///path/to/project', pattern='**/*.py'
        - Find markdown in remote bucket: path_url='s3://bucket/docs', pattern='**/*.md'
        - Find text files via HTTP: path_url='https://example.com/files', pattern='*.txt'

        Parameters
        ----------
        path_url : str
            Absolute directory URL (e.g., 'file:///path/to/dir', 's3://bucket/path', 'https://example.com/files')
        pattern : str
            Glob pattern to match (e.g., '**/*.py', '*.md')

        Returns
        -------
        GlobOutput
            Object with matches, count, and url pattern

        Raises
        ------
        ValueError
            If path_url is not a directory or pattern is malformed
        """
        parsed = self._validate_url(path_url, require_type="directory")

        search_path = parsed.path.rstrip("/") + "/" + pattern
        matches = self._fs.glob(search_path)
        url_pattern = f"{urlunparse(parsed)}/{pattern}"

        return GlobOutput(matches=matches, count=len(matches), url_pattern=url_pattern)

    async def read(self, file_url: str, offset: int | None = None, length: int | None = None) -> ReadFileOutput:
        """Read a file from the filesystem.

        Instructions:
        1. file_url MUST be an absolute file URL within the environment root (e.g., 'file:///path/to/file.txt', 's3://bucket/file.py', 'https://example.com/doc.md')
        2. All URLs must be within the environment's root URL
        3. Use glob to find files first if you don't know the exact path
        4. Offset and length are line-based (0-indexed)

        Parameters
        ----------
        file_url : str
            Absolute file URL to read (e.g., 'file:///path/to/file.txt', 's3://bucket/path/file.md', 'https://example.com/doc.py')
        offset : int | None
            Starting line number (0-indexed). If None, starts from beginning
        length : int | None
            Number of lines to read. If None, reads to end

        Returns
        -------
        ReadFileOutput
            Object with content, total lines, and lines returned

        Raises
        ------
        FileNotFoundError
            If the file doesn't exist
        ValueError
            If the file_url is malformed
        """
        parsed = self._validate_url(file_url, require_type="file")

        all_lines = self._fs.read_text(parsed.path).splitlines()

        total_lines = len(all_lines)
        start = offset if offset is not None else 0
        end = (start + length) if length is not None else total_lines

        # Get the requested slice
        selected_lines = all_lines[start:end]

        # Format with line numbers
        content = "\n".join(f"{start + i + 1:6d}\t{line}" for i, line in enumerate(selected_lines))

        return ReadFileOutput(content=content, total_lines=total_lines, lines_returned=len(selected_lines))

    async def search(
        self,
        query: str,
        path_url: str,
        search_type: SearchType = SearchType.BM25,
        filename_pattern: str | None = None,
        output_mode: OutputMode | None = None,
        case_insensitive: bool = False,
        show_line_numbers: bool = True,
        lines_before: int | None = None,
        lines_after: int | None = None,
        lines_context: int | None = None,
        limit: int = 10,
        multiline: bool = False,
    ) -> BM25Output | GrepContentOutput | GrepFilesOutput | GrepCountOutput:
        """Search documents using BM25 full-text search or regex pattern matching.

        Instructions:
        1. Use search_type='bm25' for semantic/keyword search, 'regex' for pattern matching
        2. BM25 search: Craft queries with actual terms/keywords you've seen in documents
           - Include synonyms and variations (e.g., "authenticate login session" for auth)
           - Mix general concepts with specific names (classes, functions, technical terms)
           - Results ranked by relevance score (higher = more relevant)
           - Example: query="UserAuth authenticate login", search_type="bm25"
        3. Regex search: Use regular expression patterns for precise matching
           - Pattern is a regex (not literal string)
           - Set case_insensitive=True for case-insensitive matching
           - Set multiline=True for patterns spanning multiple lines
           - Use output_mode to control results: 'content' (matches with context), 'files_with_matches' (file list), 'count' (match count)
           - Example: query="def.*\\(.*\\):", search_type="regex", output_mode="content"
        4. Use filename_pattern to filter by filename regex for both search types (e.g., '\\.py$', '.*\\.md$')
        5. For regex content mode, use lines_before/lines_after/lines_context for context lines

        Parameters
        ----------
        query : str
            For BM25: search terms (natural language). For regex: regular expression pattern
        path_url : str
            Absolute URL to file or directory to search
        search_type : SearchType
            Search type: 'bm25' for full-text search, 'regex' for pattern matching
        filename_pattern : str | None
            Regex pattern to filter filenames (e.g., '\\.py$', '.*test.*\\.js$')
        output_mode : OutputMode | None
            Regex only: 'content', 'files_with_matches', or 'count'. Ignored for BM25
        case_insensitive : bool
            Regex only: case insensitive search
        show_line_numbers : bool
            Regex content mode only: show line numbers in output
        lines_before : int | None
            Regex content mode only: lines to show before each match
        lines_after : int | None
            Regex content mode only: lines to show after each match
        lines_context : int | None
            Regex content mode only: lines before and after (overrides lines_before/after)
        limit : int
            BM25: max results to return. Regex: limit for files_with_matches/content modes
        multiline : bool
            Regex only: enable multiline mode (pattern can span lines)

        Returns
        -------
        BM25Output | GrepContentOutput | GrepFilesOutput | GrepCountOutput
            BM25Output for BM25 search, Grep outputs for regex search

        Raises
        ------
        RuntimeError
            If no index exists in the environment
        """
        if not self.index_page:
            raise RuntimeError("No search index found in environment. Create one first with 'document index' command.")

        self._validate_url(path_url)  # Validate path is within environment

        with duckdb.connect(":memory:") as conn:
            # Register filesystem
            conn.register_filesystem(self._fs)

            # Attach the index database
            conn.execute(f"ATTACH '{self.index_page}' AS idx")

            # Build filename filter using regex
            filename_filter = ""
            if filename_pattern:
                filename_filter = f"AND regexp_matches(filename, '{filename_pattern}')"

            if search_type == SearchType.BM25:
                # BM25 full-text search
                search_query = f"""
                    SELECT
                        filename,
                        fts_main_documents.match_bm25(filename, ?) AS score
                    FROM idx.documents
                    WHERE score IS NOT NULL {filename_filter}
                    ORDER BY score DESC
                    LIMIT ?
                """
                results_df = conn.execute(search_query, [query, limit]).fetchdf()

                # Convert to output format
                results = [
                    BM25Result(filename=str(row["filename"]), score=float(row["score"]))
                    for _, row in results_df.iterrows()
                ]
                return BM25Output(results=results, total_results=len(results), query=query, url_pattern=self.url)

            else:  # REGEX search
                # Default to CONTENT mode if not specified
                output_mode = output_mode or OutputMode.CONTENT

                # Build regex flags for DuckDB
                # s = dotall (. matches newline)
                regex_flags = "s" if multiline else ""
                if case_insensitive:
                    regex_flags += "i"

                if output_mode == OutputMode.FILES_WITH_MATCHES:
                    # Just get distinct filenames with matches
                    query_sql = f"""
                        SELECT DISTINCT filename
                        FROM idx.lines
                        WHERE regexp_matches(line, '{query}', '{regex_flags}') {filename_filter}
                        LIMIT {limit or -1}
                    """
                    files = [row[0] for row in conn.execute(query_sql).fetchall()]
                    return GrepFilesOutput(files=files, count=len(files))

                elif output_mode == OutputMode.COUNT:
                    # Count total matching lines
                    query_sql = f"""
                        SELECT COUNT(*)
                        FROM idx.lines
                        WHERE regexp_matches(line, '{query}', '{regex_flags}') {filename_filter}
                    """
                    result = conn.execute(query_sql).fetchone()
                    total = result[0] if result else 0
                    return GrepCountOutput(total_matches=total)

                else:  # CONTENT mode
                    before = lines_context if lines_context is not None else (lines_before or 0)
                    after = lines_context if lines_context is not None else (lines_after or 0)

                    # Get matching lines with context using window functions
                    if before > 0 or after > 0:
                        query_sql = f"""
                            WITH matches AS (
                                SELECT filename, line_number, line
                                FROM idx.lines
                                WHERE regexp_matches(line, '{query}', '{regex_flags}') {filename_filter}
                                LIMIT {limit or -1}
                            ),
                            context AS (
                                SELECT
                                    m.filename,
                                    m.line_number,
                                    m.line,
                                    LIST(l.line ORDER BY l.line_number) FILTER (WHERE l.line_number < m.line_number AND l.line_number >= m.line_number - {before}) AS before_context,
                                    LIST(l.line ORDER BY l.line_number) FILTER (WHERE l.line_number > m.line_number AND l.line_number <= m.line_number + {after}) AS after_context
                                FROM matches m
                                LEFT JOIN idx.lines l
                                    ON m.filename = l.filename
                                    AND l.line_number BETWEEN m.line_number - {before} AND m.line_number + {after}
                                GROUP BY m.filename, m.line_number, m.line
                            )
                            SELECT * FROM context
                        """
                    else:
                        query_sql = f"""
                            SELECT filename, line_number, line, NULL as before_context, NULL as after_context
                            FROM idx.lines
                            WHERE regexp_matches(line, '{query}', '{regex_flags}') {filename_filter}
                            LIMIT {limit or -1}
                        """

                    matches = conn.execute(query_sql).fetchall()

                    all_matches = [
                        GrepMatch(
                            file=filename,
                            line_number=line_num if show_line_numbers else None,
                            line=line,
                            before_context=before_ctx,
                            after_context=after_ctx,
                        )
                        for filename, line_num, line, before_ctx, after_ctx in matches
                    ]

                    return GrepContentOutput(matches=all_matches, total_matches=len(all_matches))
