---
icon: simple/markdown
---


# Markdown

Markdown files define instructions and tools for AI agents. 

## Structure

### Instructions

Declare agent instructions in the body of Markdown files.

```markdown title="README.md" hl_lines="8-12"
---
tools:
  - [ls]
  - [cat]

---

You are a helpful assistant.

## Guidelines
- Explore files with `ls`, read them with `cat`.
- Answer based on discovered tools only.
```

### Tools

List tool commands in the YAML frontmatter of Markdown files.

```markdown title="tools.md" hl_lines="1-7"
---
tools:
  - [grep]
  - [psql, -U, $USER, -d, $DB]
  - [python3, script.py]

---

# Tool Instructions
- Use `grep` for search, `psql` for queries, `python3` for analysis.
```

!!! tip "No Tools?"
    If your agent doesn't need tools, omit the frontmatter entirely and write only instructions.


## Project Layout

### README

Every application starts with a `README.md` at its root:

```bash
project/
└── README.md

0 directories, 1 file
```

### Progressive Disclosure

Agents can use tools to explore Markdown files and discover new instructions and tools.

**Example project:**

```bash
project/
├── README.md    # Has ls and cat tools
└── tools.md     # Has psql tool

0 directories, 2 files
```

**Discovery flow:**

1. Agent starts at `README.md`
2. Agent calls `ls` to discover files
3. Agent finds `tools.md`
4. Agent calls `cat tools.md` to read it
5. Agent discovers `psql` tool
6. Agent can now call `psql`

### Organization

Organize additional files however you want, for example:

**Flat structure:**

```bash
project/
├── README.md
├── search.md
└── data.csv

0 directories, 3 files
```

**Nested by feature:**

```bash
project/
├── README.md
├── database/
│   └── queries.md
├── api/
│   └── endpoints.md
└── scripts/
    └── analysis.md

3 directories, 4 files
```

**Domain-specific:**

```bash
project/
├── README.md
├── data/
│   ├── customers.csv
│   └── orders.csv
└── tools/
    ├── etl.md
    └── reporting.md

2 directories, 5 files
```