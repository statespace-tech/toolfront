---
icon: lucide/server
---

# Self-Hosting

Run applications on your own infrastructure.

## Quick start

Self-hosting uses the Rust `statespace-server` library. Build a small binary that mounts your content directory and expose it behind a reverse proxy.

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

