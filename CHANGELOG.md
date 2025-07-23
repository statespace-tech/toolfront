# Changelog

## v0.2.0 - Major SDK Refactoring

### Summary

This is a major refactoring of the architecture that exposes ToolFront as an SDK instead of a standalone MCP server. This makes ToolFront's functionality much more accessible, composable, and powerful.

### Key Features

- Built-in `ask()` method with streaming support across all data sources

- **Structured Outputs**: Type-annotated responses automatically structure data (primitives, Pydantic models, DataFrames)

- **Backward Compatibility**: Existing MCP server functionality preserved

- **Enhanced Database Support**: Added 15+ new database connectors (Athena, ClickHouse, Trino, etc.) powered by [Ibis](https://ibis-project.org/), which is a more battle-tested library for data connectivity and gives us support for more diverse datasources out-of-the-box


### Architecture Changes

- Extracted core MCP tooling logic into reusable SDK components

- Added direct LLM integration via Pydantic-AI

- Maintained MCP server as thin wrapper around SDK


### Migration Path

- MCP users: No breaking changes, existing configurations work as-is

- New users: Can use SDK directly without MCP knowledge

- Developers: Can compose ToolFront into existing applications