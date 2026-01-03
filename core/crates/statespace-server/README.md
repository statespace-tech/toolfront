# statespace-server

Open-source AI tool execution runtime. Serve markdown files with frontmatter-defined tool specifications.

## Features

- **Markdown file serving** - Serve files from a local directory with smart path resolution
- **Frontmatter parsing** - Parse YAML and TOML frontmatter for tool definitions
- **Command validation** - Validate commands against tool specifications with regex support
- **Tool execution** - Execute whitelisted tools in a sandboxed environment
- **Security** - Path traversal prevention, environment isolation, SSRF protection

## Quick Start

```bash
# Serve a tool site
statespace serve /path/to/toolsite

# Custom host and port
statespace serve /path/to/toolsite --host 0.0.0.0 --port 3000
```

## Tool Site Structure

A tool site is a directory containing markdown files with frontmatter:

```
my-toolsite/
├── README.md          # Required - served at /
├── tools/
│   ├── query.md       # Served at /tools/query
│   └── search.md      # Served at /tools/search
└── docs/
    └── README.md      # Served at /docs/
```

## Frontmatter Format

Define allowed tools in YAML or TOML frontmatter:

```yaml
---
tools:
  - [ls]                              # Allow ls with any args
  - [cat, {}]                         # cat with one arg (any value)
  - [cat, {regex: ".*\\.md$"}, ";"]   # cat only .md files, no extra args
  - [psql, -c, {regex: "^SELECT"}]    # Only SELECT queries
---

# My Tool

This tool allows file listing and viewing.
```

## HTTP API

### GET `/{path}`

Read a markdown file.

### POST `/{path}`

Execute a tool defined in frontmatter.

Request:
```json
{
  "command": ["ls", "-la", "docs/"]
}
```

Response:
```json
{
  "stdout": "total 8\n-rw-r--r-- 1 user staff 256 Jan 1 00:00 README.md\n",
  "stderr": "",
  "returncode": 0
}
```

## Library Usage

Use as a library in your own server:

```rust
use statespace_server::{build_router, ServerConfig};
use std::path::PathBuf;

let config = ServerConfig::new(PathBuf::from("./my-toolsite"))
    .with_host("0.0.0.0")
    .with_port(3000);

let router = build_router(config);
```

## Security

- **Path traversal protection** - Rejects `..` and absolute paths
- **Environment isolation** - Commands run with cleared environment
- **SSRF protection** - Blocks localhost, private IPs, cloud metadata endpoints
- **Output limits** - Prevents DoS via large output

## License

MIT OR Apache-2.0
