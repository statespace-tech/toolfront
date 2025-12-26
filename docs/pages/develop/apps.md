---
icon: lucide/layout-grid
---

# Apps

Applications combine Markdown instructions and CLI tools to create agent workflows.

## Requirements

- **Tools** - Define CLI tools as lists in the YAML frontmatters of Markdown files
- **Instructions** - Write agent instructions in body of Markdown files
- **Entry point** - All apps must have a `README.md` entry point


```yaml title="README.md"
---
tools:
  - [ls]
  - [cat]
  - [grep]
---

# Instructions
- Use `ls` to discover files
- Use `cat` to read content
- Use `grep` to search for patterns
```

> **Note**: keep everything in `README.md` for single-file apps.

## Progressive disclosure

For complex multi-file apps, agents can discover tools and instructions by exploring files:


```bash
project/
├── data/        # has .txt documents
├── README.md    # has `ls` and `cat` tools
└── tools.md     # has `grep` tool

1 directories, 10 files
```

**Example workflow**:

1. Agent starts at `README.md`
2. Calls `ls` to discover files
3. Finds `tools.md`
4. Calls `cat tools.md` to read it
5. Discovers `grep` tool
6. Can now call `grep` files in `data/`


## Data and script files

Apps can include any file type that tools can access:

```bash
project/
├── README.md
├── data/
│   ├── customers.csv
│   ├── events.parquet
│   └── logs.txt
└── scripts/
    ├── analyze.py
    └── process.sh

2 directories, 6 files
```

Tools interact with these files directly:

```yaml
---
tools:
  - [python3, scripts/analyze.py]
  - [cat, data/logs.txt]
  - [duckdb, data/events.parquet, -c, { }]
---
```

## Auto-generated files

Serving or deploying apps auto-generates three static files:

```bash hl_lines="3-5"
project/
├── README.md           # your application (required)
├── robots.txt          # auto-generated
├── favicon.svg         # auto-generated
└── index.html          # auto-generated

0 directories, 4 files
```

**index.html**

  : Landing page with human-readable connection instructions.

**robots.txt**

  : Agent-readable instructions on using the API. Embedded in `index.html`.

**favicon.svg**

  : Statespace logo displayed in browser tabs and bookmarks.

!!! warning "Advanced usage"
    Server files are auto-generated. Existing files won't be overwritten. Most users don't need to modify them.