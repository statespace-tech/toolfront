---
icon: lucide/hammer
---

# Tools

Tools give AI agents the ability to take actions by running commands.

## Syntax

Define tools as lists of commands in Markdown YAML frontmatters.

```yaml
---
tools:
  - [ls]
  - [cat]
  - [grep, -r, "error", "logs/"]
  - [curl, -X, GET, "https://api.com/v1"]
  - [python3, scripts/analyze.py]
---
```

<!-- !!! info "" -->
> By default, agents can pass additional flags or arguments to tools (e.g., `ls -la` or `cat --help`)

## Advanced usage

### Placeholders

Use `{ }` to denote where agents can pass arguments to commands.

```yaml
---
tools:
  - [cat, { }]
  - [curl, { }]
  - [grep, -r, { }, logs/]
---
```

### Regex constraints

Restrict agent arguments with `{ regex: ... }` patterns.

```yaml
---
tools:
  - [cat, { regex: ".*\.(txt|md|json)$" }]       # Only specific file types
  - [curl, { regex: "^https://api\.com/.+" }]    # Only specific domain
  - [git, checkout, { regex: "^[a-z0-9-]+$" }]   # Only valid branch names
---
```

### Options control

Add `;` at the end of a tool command to disallow additional flags and arguments.

```yaml
---
tools:
  - [cat, { }, ;]
  - [curl, { regex: "^https://api\.example\.com/.+" }, ;]
  - [rm, { regex: ".*\.tmp$" }, ;]
---
```

### Environment variables

Use environment `$VARIABLES` to hide secrets from agents, and inject them at runtime.

```yaml
---
tools:
  - command: [curl, -H, "Authorization: Bearer $API_KEY"]
  - command: [psql, -U, $USER, -d, $DATABASE, -c, { }]
---
```

!!! question "Learn more"
    Learn how to pass environment variables through the [Python SDK](../integration/python_sdk/#environment-variables), [MCP server](../integration/mcp_server/#environment-variables), [command line](../integration/command_line/#environment-variables) or [REST API](../integration/rest_api/#environment-variables).


### Custom tools

Use custom scripts and compiled binaries as tools.

**1. Add executable files to your project's repository:**

```bash hl_lines="4-5 7-8"
project/
├── README.md
├── scripts/
│   ├── analyze.py
│   └── process.sh
├── bin/
│   └── custom_tool
└── index.js

2 directories, 5 files
```

**2. Define them as tools:**

```yaml
---
tools:  
  - [python3, scripts/analyze.py]
  - [./bin/custom_tool, ;]
  - [bash, scripts/process.sh, { }, { }]
  - [node, index.js, --port, { }]
---
```

### Hooks

!!! failure "Work in progress"
    Hooks will allow you to run setup scripts and transformations automatically when deploying applications. Join our [Discord](https://discord.gg/toolfront) to stay updated and share feedback.

## Examples

### Document RAG

Search and read files in the project's repository.

```yaml
---
tools:
  - [ls]
  - [cat]
  - [tree]
  - [grep, -r, { }, { }]
---
```

### Text-to-SQL

Query a PostgreSQL database with read-only SELECT statements.

```yaml
---
tools:
  - [psql, -U, $USER, -d, $DB, -c, { regex: "^SELECT\b.*" }, ;]
---
```

### API with auth

Call external APIs with authentication headers.

```yaml
---
tools:
  - [curl, -H, "Authorization: Bearer $API_KEY"]
---
```

### Data processing

Process and analyze data with custom Python scripts.

```yaml
---
tools:
  - [python3, scripts/analyze.py]
---
```
