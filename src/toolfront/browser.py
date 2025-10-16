# import asyncio
# import json
# import logging
# from importlib.resources import files
# from typing import Any

# import yaml
# from pydantic import BaseModel, Field, field_validator
# from pydantic_ai import Agent, UnexpectedModelBehavior, models
# from pydantic_ai.mcp import MCPServerStdio
# from pydantic_ai.messages import (
#     FunctionToolCallEvent,
#     FunctionToolResultEvent,
#     PartDeltaEvent,
#     PartStartEvent,
#     TextPart,
#     TextPartDelta,
#     ThinkingPart,
#     ThinkingPartDelta,
# )
# from pydantic_ai.settings import ModelSettings
# from rich.console import Console
# from rich.live import Live
# from rich.markdown import Markdown

# from toolfront.environment import Environment
# from toolfront.utils import get_model_from_env, history_processor

# DEFAULT_TIMEOUT_SECONDS = 10
# DEFAULT_MAX_RETRIES = 3

# logger = logging.getLogger("toolfront")


# class Browser(BaseModel):
#     """A ready-to-use interface for AI agents to navigate environments and retrieve data.

#     Parameters
#     ----------
#     model : str | Model | None
#         AI model to use (e.g., "openai:gpt-5", "anthropic:claude-sonnet-4-5").
#         If not provided, uses TOOLFRONT_MODEL environment variable.
#     temperature : float, default 0.0
#         Model temperature for response generation.
#     context_window : int, default 30
#         Number of messages to keep in conversation history.
#     params : dict[str, str] | list[str] | None
#         Authentication parameters for the filesystem protocol.
#     env : dict[str, str] | list[str] | None
#         Additional environment variables to include in requests.
#     """

#     model: models.Model | models.KnownModelName | str | None = Field(None, description="AI model to use.")
#     temperature: float = Field(default=0.0, description="Model temperature.")
#     context_window: int = Field(default=30, description="Model context window.")
#     params: dict[str, str] | list[str] | None = Field(
#         None, description="Authentication parameters for the filesystem protocol", exclude=True
#     )
#     env: dict[str, str] | list[str] | None = Field(
#         None, description="Additional environment variables to include in requests.", exclude=True
#     )

#     model_config = {"arbitrary_types_allowed": True}

#     @field_validator("params", mode="before")
#     @classmethod
#     def _validate_params(cls, params: dict[str, str] | list[str] | None) -> dict[str, str] | None:
#         """Convert list of KEY=VALUE strings to dict."""
#         if isinstance(params, list):
#             return dict(param.split("=", 1) for param in params)
#         return params

#     @field_validator("env", mode="before")
#     @classmethod
#     def _validate_env(cls, env: dict[str, str] | list[str] | None) -> dict[str, str] | None:
#         """Convert list of KEY=VALUE strings to dict."""
#         if isinstance(env, list):
#             return dict(env_var.split("=", 1) for env_var in env)
#         return env

#     def __init__(
#         self,
#         model: models.Model | models.KnownModelName | str | None = None,
#         temperature: float = 0.0,
#         context_window: int = 30,
#         params: dict[str, str] | list[str] | None = None,
#         env: dict[str, str] | list[str] | None = None,
#         **kwargs,
#     ):
#         super().__init__(
#             model=model,
#             temperature=temperature,
#             context_window=context_window,
#             params=params,
#             env=env,
#             **kwargs,
#         )

#     def ask(
#         self,
#         prompt: str,
#         url: str,
#         output_type: Any = str,
#         verbose: bool = False,
#     ) -> Any:
#         """Ask natural language questions about an environment and get structured responses.

#         Parameters
#         ----------
#         prompt : str
#             Natural language question or instruction
#         url : str
#             Starting URL/path to environment (file://, https://, s3://, etc.)
#         output_type : Any | None, optional
#             Desired output type (str, int, list, Pydantic model, etc.)
#         verbose : bool, default False
#             Whether to show live AI reasoning and tool calls

#         Returns
#         -------
#         Any
#             Response in the requested output_type format. If no type specified,
#             uses type hint from caller or defaults to string.
#         """

#         environment = Environment(url=url, params=self.params, env=self.env)  # type: ignore[arg-type]

#         server = MCPServerStdio(
#             "uv",
#             args=["run", "toolfront", "mcp", "serve", url, "--transport", "stdio"],
#             env=environment.env,
#             max_retries=DEFAULT_MAX_RETRIES,
#             timeout=DEFAULT_TIMEOUT_SECONDS,
#         )

#         instructions_template = files("toolfront.instructions").joinpath("ask.txt").read_text()
#         instructions = instructions_template.format(environment.env, environment.url, environment.home_page)

#         history_processor_ = history_processor(context_window=self.context_window)

#         agent = Agent(
#             model=self.model or get_model_from_env(),
#             system_prompt=instructions,
#             toolsets=[server],
#             output_retries=DEFAULT_MAX_RETRIES,
#             output_type=output_type,
#             retries=DEFAULT_MAX_RETRIES,
#             model_settings=ModelSettings(
#                 temperature=self.temperature,
#             ),
#             history_processors=[history_processor_] if history_processor_ else None,
#         )

#         return asyncio.run(Browser._browse_async(prompt, agent, verbose))

#     @staticmethod
#     async def _browse_async(
#         prompt: str,
#         agent: Agent,
#         verbose: bool = False,
#     ) -> Any:
#         """Execute the AI agent with optional live streaming display.

#         This internal method handles the actual agent execution with two modes:
#         - Verbose: Shows live AI reasoning, tool calls, and responses in terminal
#         - Quiet: Runs silently and returns only the final result

#         Parameters
#         ----------
#         prompt : str
#             The user's natural language query
#         agent : Agent
#             Configured AI agent with tools and system prompt
#         verbose : bool, default False
#             Whether to show live updates during execution

#         Returns
#         -------
#         Any
#             The final agent response in the requested output format

#         Raises
#         ------
#         RuntimeError
#             If there's unexpected model behavior during execution
#         """

#         console = Console()

#         try:
#             if verbose:
#                 # Streaming mode with Rich Live display
#                 with Live(
#                     console=console,
#                     vertical_overflow="visible",
#                     auto_refresh=True,
#                 ) as live:
#                     accumulated_content = ""

#                     def update_display(content: str):
#                         live.update(Markdown(content))

#                     async with agent.iter(prompt) as run:
#                         async for node in run:
#                             if Agent.is_model_request_node(node):
#                                 async with node.stream(run.ctx) as model_stream:
#                                     async for event in model_stream:
#                                         if isinstance(event, PartStartEvent):
#                                             if isinstance(event.part, (TextPart | ThinkingPart)):
#                                                 accumulated_content += f"\n{event.part.content}"
#                                                 update_display(accumulated_content)
#                                         elif isinstance(event, PartDeltaEvent) and isinstance(
#                                             event.delta, (TextPartDelta | ThinkingPartDelta)
#                                         ):
#                                             accumulated_content += event.delta.content_delta or ""
#                                             update_display(accumulated_content)

#                             elif Agent.is_call_tools_node(node):
#                                 async with node.stream(run.ctx) as handle_stream:
#                                     async for event in handle_stream:
#                                         if isinstance(event, FunctionToolCallEvent):
#                                             try:
#                                                 args_str = (
#                                                     event.part.args
#                                                     if isinstance(event.part.args, str)
#                                                     else str(event.part.args)
#                                                 )
#                                                 accumulated_content += f"\n\n>Called tool `{event.part.tool_name}` with args:\n\n```yaml\n{yaml.dump(json.loads(args_str))}\n```\n\n"
#                                             except Exception:
#                                                 accumulated_content += str(event.part.args)
#                                             update_display(accumulated_content)
#                                         elif isinstance(event, FunctionToolResultEvent):
#                                             accumulated_content += f"\n\n>Tool `{event.result.tool_name}` returned:\n\n{event.result.content}\n\n"
#                                             update_display(accumulated_content)

#                             elif Agent.is_end_node(node):
#                                 return node.data.output
#             else:
#                 # Quiet mode
#                 async with agent.iter(prompt) as run:
#                     async for node in run:
#                         if Agent.is_end_node(node):
#                             return node.data.output
#         except UnexpectedModelBehavior as e:
#             logger.error(f"Unexpected model behavior: {e}", exc_info=True)
#             raise RuntimeError(f"Unexpected model behavior: {e}")
