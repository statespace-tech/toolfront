---
icon: lucide/server
---

# Self-Hosting

Run applications on your own infrastructure.

## Quick start

### Docker deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install toolfront

EXPOSE 8000
CMD ["toolfront", "app", "serve", ".", "--host", "0.0.0.0"]
```

Build and run:

```console
$ docker build -t my-app .
$ docker run -p 8000:8000 -e API_KEY=xxx my-app
```

### Reverse proxy

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name your-app.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```


## CLI reference

### `toolfront app serve`

Run applications locally or on your infrastructure.

**Usage:**

```bash
toolfront app serve [OPTIONS] PATH
```

**Arguments:**

`PATH`

: Path to application repository

**Options:**

`--host`

: Host to bind the server to (default: `127.0.0.1`)

`--port`

: Port to bind the server to (default: `8000`)

`--env KEY=VALUE`

: Environment variables to inject (can be repeated)

**Example:**

```console
$ toolfront app serve ./project --host 0.0.0.0 --port 8080 --env API_KEY=xxx
```