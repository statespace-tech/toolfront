---
icon: lucide/cloud-upload
---

# Tools

## Instructions

Add agent instructions to Markdown files.

```markdown title="README.md" hl_lines="8-14"
---
tools:
  - [ls]
  - [cat]

---

# Instructions

You are a helpful assistant.

## Guidelines
- Answer the user's question without making assumptions
- Use `ls` to explore available files, then `cat` to read them
```

### Tools

Declare executable tools in YAML frontmatters.

```markdown title="data_tools.md" hl_lines="1-9"
---
tools:
  - [grep]
  - [tree]
  - [psql, -U, $USER, -d, $DATABASE, -c, {query}]
  - [curl, -X, GET, "https://api.example.com/{endpoint}"]
  - [python3, scripts/analyze.py, --format, {format}]

---

# Tool Instructions

Use `grep`, and `tree` to explore the project's files.
Use `psql` to query the PostgreSQL database.
Use `curl` to interact with external APIs.
Use the `analyze.py` script to analyzes data.
```

#### Progressive Disclosure

Organize files any way you like. Agents can only call tools declared in Markdown files they've read.

```
project/
├── README.md
├── src/
│   ├── data_tools.md
│   └── etl_tools.md
└── data/
```

The agent explores to discover specialized tools:

1. Agent sees `README.md`.
2. Agent calls `ls` on `README.md`, sees `data_tools.md`
3. Agent calls `cat` on `data_tools.md`, discovers `psql` tool
4. Agent calls `psql` on `data_tools.md`

!!! info "Tools Are All You Need"
    You only need tools to build AI agents.

    - **Navigation tools** (`ls`, `cat`, `grep`) let agents read files and discover new instructions and tools
    - **Specialized tools** (`psql`, `python`) let agents take specific actions like querying data