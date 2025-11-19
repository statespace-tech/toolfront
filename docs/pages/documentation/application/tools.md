---
icon: lucide/hammer
---

# Tools

Tools give AI agents the ability to take actions by calling commands.

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

!!! info "Additional Arguments"
    By default, agents can pass additional flags or arguments to tools (e.g.., `ls -la` or `cat --help`)

## Advanced Usage

Add placeholders, regex constraints, and options control for fine-grained validation.

### Placeholders

Use `{{ }}` to denote where agents can pass arguments in commands.

```yaml
---
tools:
  - [cat, {{ }}]
  - [curl, {{ }}]
  - [grep, -r, {{ }}, logs/]
---
```

### Regex Constraints

Validate agent arguments with `{{ "regex" }}` patterns to restrict inputs.

```yaml
---
tools:
  - [cat, {{ ".*\.(txt|md|json)$" }}]           # Only specific file types
  - [curl, {{ "^https://api\.com/.+" }}]        # Only specific domain
  - [git, checkout, {{ "^[a-z0-9-]+$" }}]       # Only valid branch names
---
```

### Options Control

Use `;` at the end of a tool to disallow additional flags and arguments.

```yaml
---
tools:
  - [cat, {{ }}, ;]
  - [curl, {{ "^https://api\.example\.com/.+" }}, ;]
  - [rm, {{ ".*\.tmp$" }}, ;]
---
```


### Environment Variables

Use environment `$VARIABLES` to hide secrets from agents, and inject them at runtime.

```yaml
---
tools:
  - command: [curl, -H, "Authorization: Bearer $API_KEY"]
  - command: [psql, -U, $USER, -d, $DATABASE, -c {{ }}]
---
```

!!! info "Passing Environment Variables"

    Learn how to pass environment variables in the [agent documentation](integration/python_sdk/)

## Custom Tools

Use custom scripts and compiled binaries as tools.

**1. Add your scripts and binaries to the project repository:**

```bash
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
  - [bash, scripts/process.sh, {{ }}, {{ }}]
  - [node, index.js, --port, {{ }}]
---
```

!!! info "Custom Tool Support"
    Custom tools are not supported yet by Statespace Cloud. Coming soon!

## Examples

### Document RAG

Search and read files in the project's repository.

```yaml
---
tools:
  - [ls]
  - [cat]
  - [tree]
  - [grep]
---
```

### Text-to-SQL

Query a PostgreSQL database with read-only SELECT statements.

```yaml
---
tools:
  - [psql, -U, $USER, -d, $DB, -c, {{ "^SELECT\b.*" }}, ;]
---
```

### API with Auth

Call external APIs with authentication headers.

```yaml
---
tools:
  - [curl, -H, "Authorization: Bearer $API_KEY"]
---
```

### Data Processing

Process and analyze data with custom Python scripts.

```yaml
---
tools:
  - [python3, scripts/analyze.py]
---
```
