---
icon: lucide/code
---

# Coding agents

Coding agents can interact with apps by including the URL in prompts:

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

!!! warning
    Avoid connecting coding agents to public apps.
