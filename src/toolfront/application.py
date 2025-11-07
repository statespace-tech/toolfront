import asyncio
import json
from typing import Any

import httpx
import yaml
from pydantic import BaseModel, Field, HttpUrl, field_validator
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
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

from toolfront.utils import get_model_from_env, history_processor

DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MAX_RETRIES = 3


class Application(BaseModel):
    """Application for interacting with HTTP-served documentation and tools.

    Attributes
    ----------
    url : str
        HTTP/HTTPS URL to the application (e.g., https://example.com/docs/index.md)
    param : dict[str, str] | None
        Authentication parameter for remote applications
    env : dict[str, str] | None
        Environment variables for command execution
    """

    url: HttpUrl = Field(..., description="Root URL for the application")
    param: dict[str, str] | None = Field(
        default=None, description="Authentication parameter for remote applications", exclude=True
    )
    env: dict[str, str] | None = Field(default=None, description="Environment variables for commands", exclude=True)

    def __init__(
        self, url: str, param: dict[str, str] | None = None, env: dict[str, str] | None = None, **kwargs: Any
    ) -> None:
        super().__init__(url=url, param=param, env=env, **kwargs)

    @field_validator("param", mode="before")
    @classmethod
    def validate_param(cls, param: dict[str, str] | list[str] | tuple | None) -> dict[str, str] | None:
        """Convert list of KEY=VALUE strings to dict."""
        if isinstance(param, list | tuple):
            return dict(param.split("=", 1) for param in param)
        return param

    @field_validator("env", mode="before")
    @classmethod
    def validate_env(cls, env: dict[str, str] | list[str] | tuple | None) -> dict[str, str] | None:
        """Convert list of KEY=VALUE strings to dict."""
        if isinstance(env, list | tuple):
            return dict(env_var.split("=", 1) for env_var in env)
        return env

    async def action(self, url: str, command: list[str], args: dict[str, str] | None = None) -> str:
        """Execute a command from a Markdown page's frontmatter.

        This tool executes commands that must be listed in the page's frontmatter.
        Commands can parse directories, query databases, call APIs, etc.

        Instructions:
        1. url MUST ALWAYS be a complete HTTP/HTTPS URL to a file (e.g., 'https://example.com/docs/index.md')
        2. The URL must point to the specific .md file where the command is defined in the frontmatter
        3. To discover available commands and their URLs, use previously discovered/read tools and documentation
        4. IMPORTANT: You can ONLY execute commands explicitly listed in the page's frontmatter. Never call a command you haven't found in the .md file
        5. Commands must exactly match those in the frontmatter (they may include placeholders like '{endpoint}' or '{id}')
        6. If you don't know what a command does, run it with --help first (e.g., ['command', '--help'])
        7. Replace command placeholders with actual values from the args dict when executing

        Parameters
        ----------
        url : str
            Complete HTTP/HTTPS URL to the .md file where the command is defined (e.g., 'https://example.com/docs/index.md')
            MUST always be a full URL, never a file:// path
        command : list[str]
            Command and its arguments (e.g., ['curl', '-X', 'GET', 'https://api.com/{endpoint}']). REQUIRED.
        args : dict[str, str] | None
            Parameters to substitute into command placeholders (e.g., {'endpoint': 'orders', 'id': '123'})

        Returns
        -------
        str
            stdout and stderr from executing the command

        Raises
        ------
        ValueError
            If command is not provided or url is invalid
        RuntimeError
            If command is not listed in the page's frontmatter or execution fails
        """
        if not command:
            raise ValueError("command is required")

        try:
            async with httpx.AsyncClient() as client:
                payload = {"command": command}
                if args is not None:
                    payload["args"] = args
                if self.env is not None:
                    payload["env"] = self.env

                response = await client.post(
                    url,
                    json=payload,
                    headers=self.param or {},
                    timeout=DEFAULT_TIMEOUT_SECONDS,
                )
                response.raise_for_status()
                output = json.loads(response.text)
                return f"# stdout:\n\n{output.get('stdout', 'N/A')}\n\n# stderr:\n\n{output.get('stderr', 'N/A')}"
        except Exception as e:
            raise RuntimeError(f"Error executing command: {e}") from e

    def ask(
        self,
        prompt: str,
        model: models.Model | models.KnownModelName | str | None = None,
        output_type: Any = str,
        context_window: int = 30,
        verbose: bool = False,
    ) -> Any:
        """Run an agent on an application and get structured responses.

        Parameters
        ----------
        prompt : str
            Natural language instruction or command
        output_type : Any | None, optional
            Desired output type (str, int, list, Pydantic model, etc.)
        context_window : int, default 30
            Number of messages to keep in conversation history.
        verbose : bool, default False
            Whether to show live AI reasoning and tool calls

        Returns
        -------
        Any
            Response in the requested output_type format. If no type specified,
            uses type hint from caller or defaults to string.
        """

        mcp_args = ["run", "toolfront", "mcp", str(self.url), "--transport", "stdio"]
        if self.param:
            for key, value in self.param.items():
                mcp_args.extend(["--param", f"{key}={value}"])

        server = MCPServerStdio(
            "uv",
            args=mcp_args,
            env=self.env,
            max_retries=DEFAULT_MAX_RETRIES,
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )

        import time

        last_error = None
        for attempt in range(3):
            try:
                with httpx.Client() as client:
                    response = client.get(str(self.url), headers=self.param or {}, timeout=10.0)
                    response.raise_for_status()
                    instructions = response.text + f"\n\n Your current URL is: {self.url}"
                    break
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_error = e
                if attempt < 2:
                    time.sleep(5)
            except Exception as e:
                raise RuntimeError(f"Failed to read instructions from {self.url}: {e}") from e
        else:
            raise RuntimeError(f"Failed to read instructions from {self.url}: {last_error}") from last_error

        history_processor_ = history_processor(context_window=context_window)

        agent = Agent(
            model=model or get_model_from_env(),
            system_prompt=instructions,
            toolsets=[server],
            output_retries=DEFAULT_MAX_RETRIES,
            output_type=output_type,
            retries=DEFAULT_MAX_RETRIES,
            history_processors=[history_processor_] if history_processor_ else None,
        )

        return asyncio.run(Application._ask_async(prompt, agent, verbose))

    @staticmethod
    async def _ask_async(
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
            The user's natural language instruction or command
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
                                            accumulated_content += f"\n\n>Tool `{event.result.tool_name}` returned:\n\n```markdown\n{event.result.content}\n```\n\n"
                                            update_display(accumulated_content)

                            elif Agent.is_end_node(node):
                                return node.data.output
            else:
                async with agent.iter(prompt) as run:
                    async for node in run:
                        if Agent.is_end_node(node):
                            return node.data.output
        except UnexpectedModelBehavior as e:
            raise RuntimeError(f"Unexpected model behavior: {e}")
