---
icon: lucide/bot
---

# Custom agents

Build custom agents to connect to Statespace apps

## Implementation


Add an HTTP tool to your agent in your framework of choice:

=== ":simple-python: &nbsp; Python"

    ```python
    import subprocess

    @tool
    def curl_tool(url: str, args: list[str]) -> str:
        """Execute curl commands to interact with ToolFront apps."""
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
     * Execute curl commands to interact with ToolFront apps.
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

    /// Execute curl commands to interact with ToolFront apps.
    fn curl_tool(url: &str, args: Vec<&str>) -> String {
        let output = Command::new("curl")
            .args(&args)
            .arg(url)
            .output()
            .unwrap();
        String::from_utf8_lossy(&output.stdout).to_string()
    }
    ```

> **Note**: once your agent can make HTTP requests, include the app URL in prompts or instructions

## Security

### Private apps

Modify your HTTP tool to include the `Authorization` header for personal access tokens:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-app.toolfront.ai/README.md
```

### Environment variables

Modify the request body for apps using environment variables (e.g., `$API_KEY`, `$USER`):

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  https://your-app.toolfront.ai/README.md \
  -d '{
    "command": ["psql", "-c", "SELECT * FROM users"],
    "env": {"USER": "admin", "DATABASE": "prod"}
  }'
```

!!! question "Learn more"

    See the [HTTP API](api.md) for complete endpoint documentation