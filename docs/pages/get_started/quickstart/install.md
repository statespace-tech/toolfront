---
icon: lucide/download
---

# Install ToolFront

Get started in minutes with PyPI.

## Prerequisites

- **Python 3.10+**: Check with `python --version`
- **LLM Provider API Keys**: For connecting AI agents (see [supported providers](../../documentation/integration/python_sdk.md#ai-models))

## Install

Choose your package manager:

=== ":simple-python: pip"

    ```bash
    pip install toolfront
    ```

=== ":simple-uv: uv"

    ```bash
    uv add toolfront
    ```

=== ":simple-poetry: poetry"

    ```bash
    poetry add toolfront
    ```
## Verify

Test your setup:

```bash
toolfront --version
# Output: toolfront 0.3.3 (or latest)

toolfront --help
# Lists commands: serve, deploy, ask, mcp
```

---

!!! success
    You've successfully installed ToolFront. 
    
    **Next**: [build your first app](build.md)

