---
icon: lucide/waypoints
---

# REST API

The REST API enables lets you build custom client to interacting with applications over HTTP.

!!! warning "Advanced usage"
    The API is for advanced use cases. Most users should use the [SDK](python_sdk.md), [MCP](mcp_server.md), or [CLI](command_line.md) instead.

## Basic usage

### Fetch instructions

Retrieve markdown content and instructions from your application.

```bash
curl -X GET https://myapp.toolfront.app/README.md
```

### Execute tools

Execute tools defined in the application's frontmatter.

```bash
curl -X POST https://myapp.toolfront.app/README.md \
  -H "Content-Type: application/json" \
  -d '{"command": ["ls", "-la"]}'
```

## Endpoints

### GET /{path}

Fetch markdown files and resources from the application.

**Request**

```bash
curl -X GET https://myapp.toolfront.app/path/to/file.md
```

**Response**

Returns the raw markdown content with frontmatter:

```markdown
---
tools:
  - [ls]
  - [cat]
---

# Instructions

Your application documentation...
```

**Status codes**

- `200` - Success
- `403` - Forbidden (path outside served directory)
- `404` - File not found

### POST /{path}

Execute a tool defined in the file's frontmatter.

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | `array` | Yes | Command to execute (e.g., `["ls", "-la"]`) |
| `env` | `object` | No | Environment variables for the command |

**Request**

```bash
curl -X POST https://myapp.toolfront.app/README.md \
  -H "Content-Type: application/json" \
  -d '{
    "command": ["ls", "-la"],
    "env": {
      "DATABASE_URL": "postgres://localhost/mydb"
    }
  }'
```

**Response**

```json
{
  "stdout": "total 24\ndrwxr-xr-x  5 user  staff  160 Nov 19 10:30 .\n...",
  "stderr": "",
  "returncode": 0
}
```

**Response fields**

| Field | Type | Description |
|-------|------|-------------|
| `stdout` | `string` | Standard output from the command |
| `stderr` | `string` | Standard error from the command |
| `returncode` | `integer` | Exit code (0 for success) |

**Status codes**

- `200` - Success
- `400` - Invalid request (no frontmatter, no tools, empty command)
- `403` - Command not allowed (doesn't match tool definitions)
- `404` - File not found
- `408` - Command timeout
- `500` - Command execution failed

---

## Authentication

Pass authentication headers for protected applications.

```bash
curl -X GET https://myapp.toolfront.app/README.md \
  -H "Authorization: Bearer your-token-here"
```

For tool execution:

```bash
curl -X POST https://myapp.toolfront.app/README.md \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -d '{"command": ["ls"]}'
```

---

## Environment variables

Pass environment variables to tools through the request body.

```bash
curl -X POST https://myapp.toolfront.app/README.md \
  -H "Content-Type: application/json" \
  -d '{
    "command": ["psql", "-c", "SELECT * FROM users"],
    "env": {
      "DATABASE_URL": "postgres://localhost/mydb",
      "API_KEY": "secret-key"
    }
  }'
```

!!! info "Defining environment variables"
    See the [Tools documentation](../application/tools.md#environment-variables) for how to define environment variables in your tool configurations.

---

## Error handling

The API returns appropriate HTTP status codes and error messages.

**Example error response**

```json
{
  "detail": "Command not allowed: ['rm', '-rf', '/']"
}
```

**Common errors**

| Status | Description | Resolution |
|--------|-------------|------------|
| `400` | No frontmatter found | Ensure the file has YAML frontmatter with tools defined |
| `403` | Command not allowed | Verify the command matches your tool definitions |
| `404` | File not found | Check the file path exists in your application |
| `408` | Command timeout | Increase timeout or optimize the command |
| `500` | Execution failed | Check command syntax and permissions |

---

## Complete example

Building a custom client that fetches instructions and executes tools:

```python
import requests

# Base URL
base_url = "https://myapp.toolfront.app"
headers = {"Authorization": "Bearer your-token-here"}

# 1. Fetch instructions
response = requests.get(f"{base_url}/README.md", headers=headers)
instructions = response.text
print(f"Instructions: {instructions[:100]}...")

# 2. Execute a tool
response = requests.post(
    f"{base_url}/README.md",
    headers={**headers, "Content-Type": "application/json"},
    json={
        "command": ["ls", "-la"],
        "env": {"API_KEY": "secret"}
    }
)

result = response.json()
print(f"Output: {result['stdout']}")
print(f"Exit code: {result['returncode']}")
```

---

## Rate limits and timeouts

**Timeouts**

- Tool execution timeout: 30 seconds
- HTTP request timeout: 30 seconds

**Retries**

- Automatic retries: 3 attempts
- Use exponential backoff for custom clients

!!! tip "Building custom clients"
    The [Python SDK source code](https://github.com/statespace-com/toolfront) provides a reference implementation for building custom clients.
