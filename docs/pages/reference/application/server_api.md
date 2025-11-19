---
icon: lucide/box
---

# Server API

Full list of REST endpoints to interact with running applications.

!!! warning "Advanced Usage"
    This API is for advanced use cases. Most users should interact with running applications through the [Python SDK](../../documentation/integration/python_sdk.md), [MCP Server](../../documentation/integration/mcp_server.md), or [Command Line](../../documentation/integration/command_line.md) instead.

---

<div class="grid" markdown>

<div markdown>

<span class="param-tag http-get">GET</span> **`/{path}`**

Fetch Markdown/resources from the app.

**Path Parameters**

`path` <span class="param-tag param-type">string</span> <span class="param-tag param-required">required</span>

: File path (e.g., README.md)

**Headers**

Pass via `param` (e.g., Authorization: Bearer token)

**Response Attributed**

`content` <span class="param-tag param-type">string</span>

: Raw Markdown/text

</div>

<div markdown>

**Example**

```bash
curl -X GET \
  -H "Authorization: Bearer token" \
  https://fte499.toolfront.app/README.md
```

**Response**

```markdown
---
tools:
  - [ls]
  - [cat]

---
# Instructions
...
```

</div>

</div>

---

<div class="grid" markdown>

<div markdown>

<span class="param-tag http-post">POST</span> **`/{path}`**

Execute tool from frontmatter.

**Path Parameters**

`path` <span class="param-tag param-type">string</span> <span class="param-tag param-required">required</span>

: `.md` file with tool definition

**Body (JSON)**

`command` <span class="param-tag param-type">array</span> <span class="param-tag param-required">required</span>

: Command array (e.g., ["echo", "hello"])

`env` <span class="param-tag param-type">object</span> <span class="param-tag param-optional">optional</span>

: Dict overrides $VAR

**Headers**

`authorization`  <span class="param-tag param-type">string</span>

  : Bearer token

**Response Attributed**

`stdout` <span class="param-tag param-type">string</span>

: Tool standard output

`stderr` <span class="param-tag param-type">string</span>

: Tool standard error

`returncode` <span class="param-tag param-type">integer</span>

: Command exit code

</div>

<div markdown>

**Example**

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token" \
  https://app.toolfront.app/tools.md \
  -d '{
    "command": ["echo", "hello"]
  }'
```

**Response**

```json
{
  "stdout": "hello",
  "stderr": "",
  "returncode": 0
}
```

</div>

</div>

**Errors**:

- 400: No frontmatter found, no tools defined, or invalid command
- 403: Access denied (path outside served directory)
- 404: File not found