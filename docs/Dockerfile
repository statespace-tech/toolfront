# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Install system dependencies for Cairo and other image processing
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy project files (should be in build context)
COPY pyproject.toml uv.lock* ./

# Copy source code (needed for mkdocstrings)
COPY src ./src

# Install toolfront package and mkdocs dependencies
RUN uv pip install --system -e . mkdocs-material[imaging] mkdocstrings[python]

# Copy mkdocs configuration
COPY mkdocs.yml ./

# Copy docs content (everything else in current directory)
COPY documentation ./docs/documentation
COPY examples ./docs/examples
COPY reference ./docs/reference
COPY assets ./docs/assets
COPY index.md ./docs/

# Expose port 8080
EXPOSE 8080

# Run mkdocs serve
CMD ["mkdocs", "serve", "--dev-addr", "0.0.0.0:8080"]