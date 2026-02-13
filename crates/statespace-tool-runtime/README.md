# statespace-tool-runtime

Core tool execution runtime for Statespace - an open-source AI tool execution platform.

This crate provides the foundational types and execution logic for AI tools:

- **Tool parsing**: Parse commands into typed `BuiltinTool` variants
- **Frontmatter**: Parse YAML/TOML frontmatter from markdown files
- **Specification validation**: Validate commands against tool specifications
- **Execution**: Execute tools in a sandboxed environment with limits
- **Security**: SSRF protection, path traversal prevention

## Usage

```rust
use statespace_tool_runtime::{BuiltinTool, ToolExecutor, ExecutionLimits};
use std::path::PathBuf;

// Parse a command
let tool = BuiltinTool::from_command(&["cat".to_string(), "file.md".to_string()])?;

// Execute with limits
let executor = ToolExecutor::new(PathBuf::from("./my-toolsite"), ExecutionLimits::default());
let output = executor.execute(&tool).await?;
```

## Architecture

This crate follows FP-Rust patterns:

- **Pure modules** (no I/O): `frontmatter`, `spec`, `security`, `protocol`, `validation`, `tools`
- **Effectful edge**: `executor` (filesystem, subprocess, HTTP)

## License

MIT
