import asyncio
import json
import logging
import subprocess
from importlib.resources import files
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import yaml
from markitdown import MarkItDown
from pydantic import BaseModel, Field, PrivateAttr, model_validator
from pydantic_ai import Agent, UnexpectedModelBehavior, models
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.messages import (
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
    PartStartEvent,
    TextPart,
    TextPartDelta,
    ThinkingPart,
    ThinkingPartDelta,
)
from pydantic_ai.settings import ModelSettings
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

from toolfront.utils import (
    clean_url,
    get_filesystem,
    get_output_type_hint,
    history_processor,
    parse_markdown_with_frontmatter,
)

DEFAULT_TEMPERATURE = 0.0
DEFAULT_CONTEXT_WINDOW = 20
DEFAULT_MAX_RETRIES = 3

logger = logging.getLogger("toolfront")


class ToolPage(BaseModel):
    """Represents a page in an environment with executable tools and content.

    A ToolPage is a single markdown or HTML file that can contain:
    - Frontmatter with command specifications
    - Markdown content with instructions
    - Links to executable scripts/tools

    Attributes
    ----------
    url : str
        URL or file path to the page
    params : dict[str, str] | None
        Authentication parameters for filesystem protocols
    env : dict[str, str] | None
        Environment variables for command execution
    """
    url: str = Field(..., description="url of the page.")
    params: dict[str, str] | None = Field(None, description="Query parameters for the page.", exclude=True)
    env: dict[str, str] | None = Field(None, description="Environment variables for the page.", exclude=True)

    _fs: Any = PrivateAttr()
    _body: str = PrivateAttr()
    _commands: list[list[str]] | dict[str, Any] = PrivateAttr()
    _cwd: Path | str | None = PrivateAttr()
    model_config = {"arbitrary_types_allowed": True}

    @model_validator(mode="after")
    def validate_model(self):
        """Initialize the page by loading content and parsing commands.

        This method:
        1. Sets up the filesystem interface
        2. Finds and loads the appropriate file (index.md/html for directories)
        3. Parses frontmatter to extract available commands
        4. Sets the working directory for command execution

        Returns
        -------
        self : ToolPage
            The initialized ToolPage instance

        Raises
        ------
        FileNotFoundError
            If the URL points to a non-existent file or directory without an index file
        """
        self.url = clean_url(self.url)
        self._fs = get_filesystem(self.url, self.params)

        # Helper to set working directory for file:// URLs
        def set_cwd(path: str, is_dir: bool = False):
            if self.url.startswith("file://"):
                parsed_path = Path(urlparse(path).path)
                self._cwd = parsed_path if is_dir else parsed_path.parent

        # Helper to parse file content based on file extension
        def parse_file_content(content: str, file_path: str):
            if file_path.endswith(".md"):
                return parse_markdown_with_frontmatter(content)
            elif file_path.endswith((".html", ".htm")):
                md = MarkItDown()
                markdown_content = md.convert(content).text_content
                return parse_markdown_with_frontmatter(markdown_content)
            return content, []

        if self._fs.isdir(self.url):
            self.url = self.url.rstrip("/") + "/"

            # Try to find index file
            for filename in ["index.md", "index.html"]:
                index_path = urljoin(self.url, filename)
                if self._fs.isfile(index_path):
                    file_content = self._fs.read_text(index_path)
                    self._body, self._commands = parse_file_content(file_content, filename)
                    break
            else:
                raise FileNotFoundError(f"Markdown or HTML index file not found in {self.url}")

            set_cwd(self.url, is_dir=True)

        elif self._fs.isfile(self.url):
            file_content = self._fs.read_text(self.url)
            self._body, self._commands = parse_file_content(file_content, self.url)
            set_cwd(self.url, is_dir=False)

        else:
            raise FileNotFoundError(f"Not found: {self.url}")

        return self

    async def body(self) -> str:
        """Generate the complete page content including commands and their help text.

        This method:
        1. Combines the markdown body with available commands
        2. Runs each command with --help to get usage information
        3. Returns formatted content suitable for AI agent consumption

        Returns
        -------
        str
            Complete page content with commands and help text wrapped in XML tags
        """
        body = self._body
        body += "\n\n## Available commands:\n"

        if self._commands and isinstance(self._commands, list):
            body += "\n".join(f"- {c}" for c in self._commands)
            # Run all commands concurrently and collect their outputs
            outputs = await asyncio.gather(
                *(
                    self.run_command(command if isinstance(command, list) else [str(command)], help_fallback=True)
                    for command in self._commands
                )
            )

            for command, output in zip(self._commands, outputs, strict=False):
                if output:
                    body += f"\n\n### Command: `{command}`\n{output}"
        else:
            body += "N/A"

        return f"<page={self.url}>\n{body}\n</page>"

    async def run_command(self, command: list[str], help_fallback: bool = True) -> str:
        """Execute a command within the page's environment.

        Parameters
        ----------
        command : list[str]
            List of command parts (executable + arguments)
        help_fallback : bool, default True
            Whether to try --help if command fails

        Returns
        -------
        str
            Command output or help text

        Raises
        ------
        RuntimeError
            If command is not allowed or fails without help fallback
        """

        outout = []

        if isinstance(self._commands, list) and not any(
            command[: len(c)] == c for c in self._commands if isinstance(c, list)
        ):
            raise RuntimeError(f"Invalid commands: {command}. Must be one of: {self._commands}")

        result = subprocess.run(command, cwd=self._cwd, capture_output=True, text=True)

        # If command failed (no stdout but has stderr), try with --help
        if not result.stdout and result.stderr:
            if help_fallback:
                outout.append(f"Command failed: {result.stderr.strip()}. Trying --help...")

                help_result = subprocess.run(command + ["--help"], cwd=self._cwd, capture_output=True, text=True)
                if not help_result.stdout and help_result.stderr:
                    raise RuntimeError(f"Command failed: {result.stderr.strip()}")

                outout.append(f"Command --help:\n{help_result.stdout.strip()}")
            else:
                raise RuntimeError(f"Command failed: {result.stderr.strip()}")
        else:
            outout.append(result.stdout.strip() or "N/A")

        return "\n".join(outout)


class Browser(BaseModel):
    """Interface for navigating and interacting with environments."""

    model: models.Model | models.KnownModelName | str | None = Field(None, description="AI model to use.")
    temperature: float = Field(default=DEFAULT_TEMPERATURE, description="Model temperature.")
    context_window: int = Field(default=DEFAULT_CONTEXT_WINDOW, description="Model context window.")
    params: dict[str, str] | None = Field(
        None, description="Authentication parameters for the filesystem protocol", exclude=True
    )
    env: dict[str, str] | None = Field(
        None, description="Additional environment variables to include in requests.", exclude=True
    )

    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        model: models.Model | models.KnownModelName | str | None = None,
        temperature: float = DEFAULT_TEMPERATURE,
        context_window: int = DEFAULT_CONTEXT_WINDOW,
        params: dict[str, str] | None = None,
        env: dict[str, str] | None = None,
        **kwargs,
    ):
        super().__init__(
            model=model,
            temperature=temperature,
            context_window=context_window,
            params=params,
            env=env,
            **kwargs,
        )

    def ask(
        self,
        prompt: str,
        url: str,
        output_type: BaseModel | None = None,
        verbose: bool = False,
    ) -> Any:
        """Ask natural language questions about an environment and get structured responses.

        Parameters
        ----------
        prompt : str
            Natural language question or instruction
        url : str
            Starting URL/path to environment (file://, https://, s3://, etc.)
        output_type : BaseModel | None, optional
            Desired output type (str, int, list, Pydantic model, etc.)
        verbose : bool, default False
            Whether to show live AI reasoning and tool calls

        Returns
        -------
        Any
            Response in the requested output_type format. If no type specified,
            uses type hint from caller or defaults to string.

        Example
        -------
        Simple string response:

        ```python
        result = browser.ask("Who is best customer?", "s3://path/to/site")
        # Returns: "Chimex Inc. seems to have the highest revenue"
        ```

        Example
        -------
        Typed response:

        ```python
        count: float = browser.ask("What's our Q3 revenue?", "s3://analytics-bucket/path/to/reports")
        # Returns: 225000.3
        ```

        Example
        -------
        Structured response:

        ```python
        from pydantic import BaseModel

        class Authors(BaseModel):
            authors: list[str]

        authors: Authors = browser.ask("List all authors in this project", "git://path/to/site")

        # Returns: Authors(authors=["Alice Smith", "Bob Jones", "Carol Lee"])
        ```
        """

        # Get the output type from the caller or use the default output type
        output_type_hint = get_output_type_hint()
        if output_type_hint:
            output_type = output_type_hint  # type: ignore
        elif output_type is None:
            output_type = str  # type: ignore

        server = MCPServerStdio(
            "uv",
            args=["run", "toolfront", "browser", "serve", url, "--transport", "stdio"],
            env=self.env,
            max_retries=DEFAULT_MAX_RETRIES,
            log_level=None,
            timeout=10,
        )

        instruction_file = files("toolfront") / "instructions" / "ask.txt"
        instructions = instruction_file.read_text()

        # Add starting page instructions
        page = ToolPage(url=url, params=self.params, env=self.env)
        instructions += asyncio.run(page.body())

        if self.env:
            instructions += "\n\n## Available env vars:\n" + "\n".join(f"- {c}" for c in self.env)

        agent = Agent(
            model=self.model,
            system_prompt=instructions,
            toolsets=[server],
            output_retries=DEFAULT_MAX_RETRIES,
            output_type=output_type,  # type: ignore
            retries=DEFAULT_MAX_RETRIES,
            model_settings=ModelSettings(
                temperature=self.temperature,
            ),
            history_processors=[history_processor(context_window=self.context_window)]
            if history_processor(context_window=self.context_window)
            else None,  # type: ignore
        )

        return asyncio.run(Browser._browse_async(prompt, agent, verbose))

    @staticmethod
    async def _browse_async(
        prompt: str,
        agent: Agent,
        verbose: bool = False,
    ) -> Any:
        """Execute the AI agent with optional live streaming display.

        This internal method handles the actual agent execution with two modes:
        - Verbose: Shows live AI reasoning, tool calls, and responses in terminal
        - Quiet: Runs silently and returns only the final result

        Parameters
        ----------
        prompt : str
            The user's natural language query
        agent : Agent
            Configured AI agent with tools and system prompt
        verbose : bool, default False
            Whether to show live updates during execution

        Returns
        -------
        Any
            The final agent response in the requested output format

        Raises
        ------
        RuntimeError
            If there's unexpected model behavior during execution
        """

        console = Console()

        try:
            if verbose:
                # Streaming mode with Rich Live display
                with Live(
                    console=console,
                    vertical_overflow="visible",
                    auto_refresh=True,
                ) as live:
                    accumulated_content = ""

                    def update_display(content: str):
                        live.update(Markdown(content))

                    async with agent.iter(prompt) as run:
                        async for node in run:
                            if Agent.is_model_request_node(node):
                                async with node.stream(run.ctx) as model_stream:
                                    async for event in model_stream:
                                        if isinstance(event, PartStartEvent):
                                            if isinstance(event.part, (TextPart | ThinkingPart)):
                                                accumulated_content += f"\n{event.part.content}"
                                                update_display(accumulated_content)
                                        elif isinstance(event, PartDeltaEvent) and isinstance(
                                            event.delta, (TextPartDelta | ThinkingPartDelta)
                                        ):
                                            accumulated_content += event.delta.content_delta or ""
                                            update_display(accumulated_content)

                            elif Agent.is_call_tools_node(node):
                                async with node.stream(run.ctx) as handle_stream:
                                    async for event in handle_stream:
                                        if isinstance(event, FunctionToolCallEvent):
                                            try:
                                                args_str = (
                                                    event.part.args
                                                    if isinstance(event.part.args, str)
                                                    else str(event.part.args)
                                                )
                                                accumulated_content += f"\n\n>Called tool `{event.part.tool_name}` with args:\n\n```yaml\n{yaml.dump(json.loads(args_str))}\n```\n\n"
                                            except Exception:
                                                accumulated_content += str(event.part.args)
                                            update_display(accumulated_content)
                                        elif isinstance(event, FunctionToolResultEvent):
                                            accumulated_content += f"\n\n>Tool `{event.result.tool_name}` returned:\n\n{event.result.content}\n\n"
                                            update_display(accumulated_content)

                            elif Agent.is_end_node(node):
                                return node.data.output
            else:
                # Quiet mode
                async with agent.iter(prompt) as run:
                    async for node in run:
                        if Agent.is_end_node(node):
                            return node.data.output
        except UnexpectedModelBehavior as e:
            logger.error(f"Unexpected model behavior: {e}", exc_info=True)
            raise RuntimeError(f"Unexpected model behavior: {e}")
