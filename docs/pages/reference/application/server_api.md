---
icon: lucide/box
---

# Server API

REST API endpoints for interacting with running RAG applications.

!!! warning "Advanced usage"
    This API is for advanced use cases. Most users should instead interact with applications through the [Python SDK](../../documentation/integration/python_sdk.md), [MCP server](../../documentation/integration/mcp_server.md), or [Command line](../../documentation/integration/command_line.md).

<div class="grid" markdown>

<div markdown>

<span class="param-tag http-get">GET</span> **`/{path}`**

Read a file from the application directory.

**Path parameters**

`path` <span class="param-tag param-type">string</span> <span class="param-tag param-required">required</span>

: Path to markdown file (e.g., `README.md` or `src/file.txt`)

**Headers**

`authorization`  <span class="param-tag param-type">string</span>

  : Bearer token for authentication

**Response**

: Raw file content

</div>

<div markdown>

**Example**

```bash
curl -X GET \
  -H "Authorization: Bearer token" \
  https://127.0.0.1:8000/README.md
```

**Example Response**

```yaml
---
tools:
  - [ls]
  - [cat]
---

# Instructions
You are an AI agent.
```

</div>

</div>

<div class="grid" markdown>

<div markdown>

<span class="param-tag http-post">POST</span> **`/{path}`**

Execute a tool defined in a Markdown's frontmatter.

**Path parameters**

`path` <span class="param-tag param-type">string</span> <span class="param-tag param-required">required</span>

: Path to markdown file containing the tool definition

**Request body (JSON)**

`command` <span class="param-tag param-type">array</span> <span class="param-tag param-required">required</span>

: Command to execute as an array of strings (e.g., `["echo", "hello"]`)

`env` <span class="param-tag param-type">object</span> <span class="param-tag param-optional">optional</span>

: Environment variables to pass to the command (e.g., `{"USER": "john"}`)

**Headers**

`authorization`  <span class="param-tag param-type">string</span>

  : Bearer token for authentication

**Response (JSON)**

`stdout` <span class="param-tag param-type">string</span>

: Standard output from the command

`stderr` <span class="param-tag param-type">string</span>

: Standard error from the command

`returncode` <span class="param-tag param-type">integer</span>

: Exit code (0 for success, non-zero for errors)

</div>

<div markdown>

**Example**

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token" \
  https://127.0.0.1:8000/README.md \
  -d '{
    "command": ["echo", "hello"]
  }'
```

**Example Response**

```json
{
  "stdout": "hello",
  "stderr": "",
  "returncode": 0
}
```

</div>

</div>