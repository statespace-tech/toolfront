FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    git \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./
COPY src ./src

RUN uv pip install --system -e . zensical

COPY zensical.toml ./

COPY pages ./docs/pages
COPY assets ./docs/assets
COPY index.md ./docs/

EXPOSE 8080

CMD ["zensical", "serve", "--dev-addr", "0.0.0.0:8080"]
