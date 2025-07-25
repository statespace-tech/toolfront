import asyncio
import json
import logging
from abc import ABC, abstractmethod
from contextvars import ContextVar
from importlib.resources import files
from typing import Any, Self

import pandas as pd
import yaml
from pydantic import BaseModel, Field
from pydantic_ai import Agent, Tool, UnexpectedModelBehavior, models
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
from rich.panel import Panel
from rich.text import Text

from toolfront.config import MAX_RETRIES
from toolfront.utils import (
    deserialize_response,
    get_default_model,
    get_output_type_hint,
    prepare_tool_for_pydantic_ai,
    type_allows_none,
)

logger = logging.getLogger("toolfront")
console = Console()

# Type aliases for AI response types
BasicTypes = str | bool | int | float
Collections = list[Any] | set[Any] | tuple[Any, ...] | dict[str, Any]
AIResponse = dict[str, Any] | BasicTypes | Collections | BaseModel | pd.DataFrame

# Context variable to store datasources for the current context
_context_datasources: ContextVar[dict[str, "DataSource"] | None] = ContextVar("context_datasources", default=None)


class CallerContext(BaseModel):
    """Context information about the caller of a method."""

    var_name: str | None = Field(None, description="The name of the variable that will be assigned the response")
    var_type: Any = Field(None, description="The type of the variable that will be assigned the response")
    context: str | None = Field(None, description="Formatted caller context string")


class DataSource(BaseModel, ABC):
    """Abstract base class for all datasources."""

    def __repr__(self) -> str:
        dump = self.model_dump()
        args = ", ".join(f"{k}={repr(v)}" for k, v in dump.items())
        return f"{self.__class__.__name__}({args})"

    def __str__(self) -> str:
        return self.__repr__()

    @classmethod
    def from_url(cls, url: str) -> Self:
        if url.startswith("http"):
            from toolfront.models.api import API

            return API(spec=url)
        elif url.startswith("file"):
            if url.endswith(".json") or url.endswith(".yaml") or url.endswith(".yml"):
                from toolfront.models.api import API

                return API(spec=url)
            else:
                from toolfront.models.document import Document

                return Document(filepath=url)
        else:
            from toolfront.models.database import Database

            return Database(url=url)

    @classmethod
    def load_from_sanitized_url(cls, sanitized_url: str) -> Self:
        context_cache = _context_datasources.get() or {}
        if sanitized_url not in context_cache:
            raise ValueError(f"Datasource {sanitized_url} not found")

        obj = context_cache[sanitized_url]
        if not isinstance(obj, cls):
            raise ValueError(f"Datasource {sanitized_url} is not a {cls.__name__}")
        return obj

    @abstractmethod
    def tools(self) -> list[callable]:
        raise NotImplementedError("Subclasses must implement tools")

    def ask(
        self,
        prompt: str,
        model: models.Model | models.KnownModelName | str | None = None,
        context: str | None = None,
        stream: bool = False,
    ) -> AIResponse:
        """
        Ask the datasource a question and return the result.

        Parameters
        ----------
        prompt : str
            The question or instruction to ask the datasource.
        model : models.Model | models.KnownModelName | str | None, optional
            The model to use. If None, uses the default model.
        context : str | None, optional
            Additional context to provide to the model.
        stream : bool, optional
            Whether to display live streaming output in the terminal. Defaults to False.

            **Why streaming is off by default:**
            - SDKs should be "quiet by default" - they shouldn't print to stdout unless explicitly requested
            - Prevents unexpected output in production/automation environments
            - Follows the principle of least surprise for programmatic use
            - Users can easily enable streaming when desired for debugging or interactive exploration

        Returns
        -------
        AIResponse
            The response from the datasource, which can be a string, dict, list, DataFrame, or Pydantic model.
        """

        if model is None:
            model = get_default_model()

        # Get caller context and add it to the system prompt
        output_type = get_output_type_hint() or str
        if output_type:
            output_type = self._preprocess(output_type)

        system_prompt = self.instructions(context=context)
        tools = [Tool(prepare_tool_for_pydantic_ai(tool), max_retries=MAX_RETRIES) for tool in self.tools()]

        agent = Agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
            output_retries=MAX_RETRIES,
            output_type=output_type | None,
        )

        result = asyncio.run(self._ask_async(prompt, agent, stream))

        if result is None and not type_allows_none(output_type):
            raise RuntimeError(
                f"ask() failed and returned None but output type {output_type.__name__} does not allow None values. "
                f"To fix this, update the type annotation to allow None e.g. answer: {output_type.__name__} | None = ask(...)"
            )

        return self._postprocess(result)

    def _preprocess(self, var_type: Any) -> Any:
        return var_type

    def _postprocess(self, result: Any) -> Any:
        return result

    def instructions(self, context: str | None = None) -> str:
        """
        Get the context for the datasource.
        """
        instruction_file = files("toolfront") / "instructions" / "ask.txt"

        with instruction_file.open() as f:
            agent_instruction = f.read()

        if context:
            agent_instruction += f"\n\nThe user has provided the following information:\n\n{context}"

        return (
            f"{agent_instruction}\n\n"
            f"Use the following information about the user's data to guide your response:\n\n"
            f"{yaml.dump(self.model_dump())}"
        )

    async def _ask_async(
        self,
        prompt: str,
        agent: Agent,
        stream: bool = False,
    ) -> AIResponse:
        """
        Run the agent and optionally stream the response with live updating display.
        Returns the final result from the agent.
        """

        panel_title = f"[bold green]{str(self)}[/bold green]"

        try:
            if stream:
                # Streaming mode with Rich Live display
                with Live(
                    Panel(
                        Text("Thinking...", style="dim white"),
                        title=panel_title,
                        border_style="green",
                    ),
                    refresh_per_second=10,
                ) as live:
                    accumulated_content = ""

                    def update_display(content: str):
                        live.update(Panel(Markdown(content), title=panel_title, border_style="green"))

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
                                            accumulated_content += event.delta.content_delta
                                            update_display(accumulated_content)

                            elif Agent.is_call_tools_node(node):
                                async with node.stream(run.ctx) as handle_stream:
                                    async for event in handle_stream:
                                        if isinstance(event, FunctionToolCallEvent):
                                            try:
                                                accumulated_content += f"\n\n>Called tool `{event.part.tool_name}` with args:\n\n```yaml\n{yaml.dump(json.loads(event.part.args))}\n```\n\n"
                                            except Exception:
                                                accumulated_content += event.part.args
                                            update_display(accumulated_content)
                                        elif isinstance(event, FunctionToolResultEvent):
                                            tool_result = deserialize_response(event.result.content)
                                            accumulated_content += (
                                                f"\n\n>Tool `{event.result.tool_name}` returned:\n\n{tool_result}\n\n"
                                            )
                                            update_display(accumulated_content)

                            elif Agent.is_end_node(node):
                                return node.data.output
            else:
                # Quiet mode - just run the agent without display
                async with agent.iter(prompt) as run:
                    async for node in run:
                        if Agent.is_end_node(node):
                            return node.data.output
        except UnexpectedModelBehavior as e:
            logger.error(f"Unexpected model behavior: {e}", exc_info=True)
            raise RuntimeError(f"Unexpected model behavior: {e}")
