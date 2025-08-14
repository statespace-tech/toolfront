# API Integration

ToolFront connects to any REST API that provides an [OpenAPI](https://www.openapis.org/) (formerly Swagger) specification.

!!! tip "OpenAPI is Everywhere!"
    Most APIs you're familiar with, like Slack, Discord, Salesforce, and PayPal, provide an OpenAPI specification. 



---

## Connecting an API

Connect to an API by providing an OpenAPI spec URL, file path, or dictionary.

=== ":fontawesome-solid-link:{.middle} &nbsp; URL Spec"

    ```python linenums="1"
    from toolfront import API

    # Pass the OpenAPI spec URL
    api = API(spec="http://localhost:8000/openapi.json")

    result = api.ask("Get summary of Python programming language")
    ```

=== ":fontawesome-solid-folder:{ .middle } &nbsp; File Spec"

    ```python linenums="1"
    from toolfront import API

    # Pass the OpenAPI spec filepath
    api = API(spec="file:///path/to/openapi.yaml")

    result = api.ask("List all active users")
    ```

=== ":fontawesome-solid-code:{ .middle } &nbsp; Dictionary Spec"

    ```python linenums="1"
    from toolfront import API

    spec = {
        "openapi": "3.0.0",
        "servers": [{"url": "https://api.example.com"}],
        "paths": {
            "/users": {"get": {"summary": "Get users"}}
        }
    }

    # Pass the OpenAPI spec as a dictionary
    api = API(spec=spec)
    result = api.ask("Get user information")
    ```

---

## Authentication

Pass authentication details using `headers` and `params` parameters to include them in all HTTP requests for the API.

```python linenums="1"
from toolfront import API

# Custom headers and query parameters
api = API(
    "https://api.example.com/spec.json",
    headers={
        "Authorization": "Bearer your-token",
        "X-API-Key": "your-api-key",
        "Content-Type": "application/json"
    },
    params={"format": "json", "version": "v1"}
)

result = api.ask("List all active users")
```