---
icon: lucide/wrench
---

# CLI tools

Give AI agents the ability to take actions by running CLI tools.

## Usage

Define CLI tools as lists in the YAML frontmatters of Markdown files.

```yaml hl_lines="1-8"
---
tools:
  - [ls]
  - [cat]
  - [grep, -r, "error", "logs/"]
  - [curl, -X, GET, "https://api.com/v1"]
  - [python3, scripts/analyze.py]
---

# Instructions
- Use the provided tools to explore and analyze
```

> **Note**: by default, agents can append additional arguments to tools (e.g., `ls -la` or `cat --help`)

## Navigation

Use navigation toolss to progressively discover more tools and instructions:

```yaml
---
tools:
  - [ls]
  - [cat]
  - [tree]
  - [grep]
  - [find]
---

# Instructions
- Use the provided tools to find more tools
```

## Placeholders

Use `{ }` to denote where agents can pass arguments to commands.

```yaml
---
tools:
  - [cat, { }]                      # agent passes file name
  - [grep, -r, { }, logs/]          # agent passes search term
  - [curl, -X, POST, { }, -d, { }]  # agent passes URL and data
---
```

## Regex constraints

Restrict tool arguments with `{ regex: ... }` patterns.

```yaml
--- 
tools:
  - [rm, { regex: ".*\.(txt|md|json)$" }]                 # file type restrictions
  - [curl, { regex: "^https://(api\.company\.com)/.+" }]  # URL restrictions
  - [psql, -c, { regex: "^SELECT\b.*" }]                  # SQL safety (read-only)
  - [ls, { regex: "^/home/user/.*" }]                     # path restrictions
  - [git, checkout, { regex: "^[a-z0-9-]+$" }]            # valid branch names
---
```

## Options control

Add `;` at the end of a tool command to disallow additional flags and arguments.

```yaml
---
tools:
  - [cat, { }, ;]
  - [curl, -X, GET, "https://api.com", ;]
  - [rm, { regex: ".*\.png$" }, ;]
---
```

> **Note**: CLI tools run directly without shell interpretation, preventing command injection attacks

## Environment variables

Use environment `$VARIABLES` to hide secrets from agents and inject them at runtime.

```yaml
---
tools:
  - [curl, -H, "Authorization: Bearer $API_KEY", "https://api.com"]
  - [psql, -U, $USER, -d, $DATABASE, -c, { }]
---
```

## Custom tools

Use custom scripts and compiled binaries as tools.

**1. Add executable files to your project:**

```bash hl_lines="4-6"
project/
├── README.md
└── custom/
    ├── analyze.py
    └── process.sh
    └── index.js

1 directories, 4 files
```

**2. Define them as tools:**

```yaml
---
tools:
  - [python3, scripts/analyze.py]
  - [bash, scripts/process.sh, { }, { }]
  - [node, index.js, --port, { }]
---
```