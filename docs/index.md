---
icon: lucide/home
---

<p align="center">
  <a href="https://github.com/statespace-tech/toolfront">
    <img src="assets/images/favicon.svg" alt="ToolFront" style="width:20%;">
  </a>
</p>
<div align="center">
    <h1 style="font-weight: 800;"><b>ToolFront</b></h1>
</div>
<p align="center">
    <em>
      Turn your data into shareable LLM apps in minutes. All in pure Markdown. Zero boilerplate.
    </em>
</p>

<p align="center">
  <a href="https://github.com/statespace-tech/toolfront/actions/workflows/test.yml" target="_blank" style="text-decoration: none;">
    <img src="https://github.com/statespace-tech/toolfront/actions/workflows/test.yml/badge.svg" alt="Test Suite">
  </a>
  <a href="https://www.python.org/downloads/" target="_blank" style="text-decoration: none;">
    <img src="https://img.shields.io/badge/python-3.10+-3775A9?style=flat-square" alt="Python 3.10+">
  </a>
  <a href="https://pypi.org/project/toolfront/" target="_blank" style="text-decoration: none;">
    <img src="https://img.shields.io/pypi/v/toolfront?color=3775A9&label=pypi%20package&style=flat-square" alt="PyPI package">
  </a>
  <a href="https://github.com/statespace-tech/toolfront/blob/main/LICENSE" target="_blank" style="text-decoration: none;">
    <img src="https://img.shields.io/badge/license-MIT-007ec6?style=flat-square" alt="License">
  </a>
  <a href="https://discord.gg/rRyM7zkZTf" target="_blank" style="text-decoration: none;">
    <img src="https://img.shields.io/discord/1323415085011701870?label=Discord&logo=discord&logoColor=white&color=5865F2&style=flat-square" alt="Discord">
  </a>
  <a href="https://x.com/statespace_tech" target="_blank" style="text-decoration: none;">
    <img src="https://img.shields.io/badge/Statespace-black?style=flat-square&logo=x&logoColor=white" alt="X">
  </a>
</p>

---

**Source code: [https://github.com/statespace-tech/toolfront](https://github.com/statespace-tech/toolfront)**

---

_ToolFront is a declarative framework for building modular LLM applications in Markdown._

## Example

### Create it

Start with one file: `README.md`


```yaml title="README.md"
---
tools:
  - [date]
---

# Instructions
- Run `date` to check today's date
```

### Serve it

Run your app locally:

```console
$ toolfront serve .
```
> **Note**: Runs on `http://127.0.0.1:8000`

### Ask it

Include the app URL in your prompts:

=== ":simple-claude: &nbsp; Claude Code"

    ```console
    $ claude "Get today's date from http://127.0.0.1:8000"
    ```

=== ":simple-githubcopilot: &nbsp; GitHub Copilot"

    ```console
    $ copilot "Get today's date from http://127.0.0.1:8000"
    ```

=== ":simple-openai: &nbsp; Codex"

    ```console
    $ codex "Get today's date from http://127.0.0.1:8000"
    ```

For custom agents, add an HTTP request tool:

=== ":simple-python: &nbsp; Python"

    ```python
    import subprocess

    @tool
    def curl_tool(url: str, args: list[str]) -> str:
        """Execute curl commands to interact with Statespace apps."""
        result = subprocess.run(
            ['curl', *args, url],
            capture_output=True,
            text=True
        )
        return result.stdout
    ```

=== ":simple-typescript: &nbsp; TypeScript"

    ```typescript
    import { execFileSync } from 'child_process';

    /**
     * Execute curl commands to interact with Statespace apps.
     */
    function curlTool(url: string, args: string[]): string {
        const result = execFileSync('curl', [...args, url], {
            encoding: 'utf-8'
        });
        return result.toString();
    }
    ```

=== ":simple-rust: &nbsp; Rust"

    ```rust
    use std::process::Command;

    /// Execute curl commands to interact with HTTP endpoints.
    fn curl_tool(url: &str, args: Vec<&str>) -> String {
        let output = Command::new("curl")
            .args(&args)
            .arg(url)
            .output()
            .unwrap();
        String::from_utf8_lossy(&output.stdout).to_string()
    }
    ```

## Complex example

### Upgrade it

Your app can grow into a full project:

```bash
project/
├── README.md
├── data/
│   ├── log1.txt
│   ├── log2.txt
│   └── log3.txt
└── src/
    ├── agentic_rag.md
    ├── text2sql.md
    └── vector_search.md

3 directories, 9 files
```

Update `README.md` with CLI tools to progressively discover and read other files:

```yaml title="README.md" hl_lines="4-5 10"
---
tools:
  - [date]
  - [ls]
  - [cat]
---

# Instructions
- Run `date` to check today's date
- Use `ls` and `cat` to discover and read other files
```

### Compose it

Add pages and CLI tools for different workflows:

=== ":lucide-list-indent-increase: &nbsp; Vector Search"

    ```yaml title="src/vector_search.md"
    ---
    tools:
      - [curl, -X, POST, https://host.pinecone.io/records/namespaces/user/search]
    ---

    # Vector search instructions:
    - Query documents with your vector database API
    ```

    > **Note**: replace the API with your own (e.g., Pinecone, Weaviate, Qdrant)

=== ":lucide-database: &nbsp; Text-to-SQL"

    ```yaml title="src/text2sql.md"
    ---
    tools:
      - [psql, -U, $USER, -d, $DB, -c, { regex: "^SELECT\b.*" }]
    ---

    # Text-to-SQL instructions:
    - Use `psql` for read-only PostgreSQL queries
    ```

    > **Note**: use your own database CLI (e.g., `mysql`, `sqlite3`, `mongosh`).

=== ":lucide-bot: &nbsp; Agentic RAG"

    ```yaml title="src/agentic_LLM.md"
    ---
    tools:
      - [grep, -r, -i, { }, ../data/]
    ---

    # Document search instructions:
    - Use `grep` to search documents in `../data/`
    ```

    > **Note**: apps can include any file type (e.g. `.csv`, `.sqlite`, `.json`)

### Deploy it

Create a free [Statespace account](https://statespace.com/) to deploy authenticated private apps:

```console
$ toolfront deploy . --private
```

Alternatively, share public apps with the community:

```console
$ toolfront deploy . --public
```
> **Note** Statespace gives you app URLs you can paste in prompts and instructions.

## Installation

Install `toolfront` with your favorite PyPI package manager:

=== ":fontawesome-brands-python: &nbsp; pip"

    ```console
    $ pip install toolfront
    ```

=== ":simple-uv: &nbsp; uv"

    ```console
    $ uv add toolfront
    ```

=== ":simple-poetry: &nbsp; poetry"

    ```console
    $ poetry add toolfront
    ```