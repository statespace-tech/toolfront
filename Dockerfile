# ToolFront MCP Server Docker Image
FROM python:3.11.11-slim

# Create a non-root user and group
RUN groupadd -r appgroup && useradd --no-log-init -r -m -g appgroup appuser

# Set the working directory for the application
WORKDIR /app

# Give appuser ownership of the WORKDIR
RUN chown appuser:appgroup /app

# Install system dependencies and uv (as root, before switching user)
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libpq-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv==0.5.2

# Create virtual environment, initially as root, then chown to appuser
ENV VIRTUAL_ENV=/app/venv
RUN python -m venv $VIRTUAL_ENV && chown -R appuser:appgroup $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy project files and set ownership
COPY --chown=appuser:appgroup pyproject.toml ./
COPY --chown=appuser:appgroup src/ src/
COPY --chown=appuser:appgroup README.md ./

# Switch to non-root user
USER appuser

# Install Python dependencies using uv in the virtual environment
RUN uv pip install --no-cache .[all]

# Entrypoint script
COPY --chmod=755 --chown=appuser:appgroup <<'EOF' /app/entrypoint.sh
#!/bin/sh
set -e

echo "Starting ToolFront MCP server with args: $@"
exec toolfront "$@"
EOF

ENTRYPOINT ["/app/entrypoint.sh"]
CMD []
