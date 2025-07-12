import asyncio
import logging
import os
from functools import wraps
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import diskcache
from platformdirs import user_cache_dir
from sqlalchemy.engine.url import make_url

from toolfront.models.connections.api import APIConnection
from toolfront.models.connections.database import DatabaseConnection
from toolfront.models.connections.library import LibraryConnection
from toolfront.types import DatasourceType

logger = logging.getLogger("toolfront")

cache_dir = user_cache_dir("toolfront")
_cache = diskcache.Cache(cache_dir)


def get_datasource_type(url: str) -> DatasourceType:
    """Analyze URL and return its type."""
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme

    if scheme in ("http", "https"):
        return DatasourceType.API

    elif scheme == "file":
        path = Path(parsed_url.path)
        if path.exists():
            if path.is_file() and path.suffix.lower() in [".json", ".yaml", ".yml"]:
                return DatasourceType.API
            elif path.is_dir():
                return DatasourceType.LIBRARY

        raise ConnectionError(f"Path does not exist: {path}")

    else:
        return DatasourceType.DATABASE


def save_to_env(key: str, value: str) -> bool:
    """Save a value to the environment."""
    return os.environ.setdefault(key, value)


def load_from_env(key: str) -> str | None:
    """Load a value from the environment."""
    return os.getenv(key, key)


def save_to_cache(key: str, value: Any, expire: int = None) -> bool:
    """Cache an object with TTL."""
    return _cache.set(key, value, expire=expire)


def load_from_cache(key: str) -> Any | None:
    """Load an object from the cache."""
    return _cache.get(key)


# Connection Management
async def save_connections(urls: list[str] | str) -> list[str] | str:
    """Save connections and return clean/obfuscated URLs."""

    async def save_connection(url: str) -> str:
        datasource_type = get_datasource_type(url)

        if datasource_type == DatasourceType.API:
            url = await _handle_api_connection(url)
        elif datasource_type == DatasourceType.LIBRARY:
            url = await _handle_library_connection(url)
        elif datasource_type == DatasourceType.DATABASE:
            url = await _handle_database_connection(url)
        else:
            raise ConnectionError(f"Unsupported datasource: {datasource_type}")

        logger.info(f"Successfully connected to {url}")
        return url

    async def _handle_api_connection(spec_url: str) -> str:
        """Handle file-based API connection logic."""
        from toolfront.models.spec import Spec

        spec = Spec.from_spec_url(spec_url)
        api_url = spec.url

        # Cache the spec using the api_url as key (not spec_url) so APIConnection can find it
        save_to_cache(api_url, spec.model_dump())

        result = await APIConnection.test_connection(api_url)
        if result.connected:
            return api_url
        else:
            raise ConnectionError(f"Failed to connect to {spec_url}: {result.message}")

    async def _handle_library_connection(url: str) -> str:
        """Handle library connection logic."""
        result = await LibraryConnection.test_connection(url)
        if result.connected:
            return url
        else:
            raise ConnectionError(f"Failed to connect to {url}: {result.message}")

    async def _handle_database_connection(url: str) -> str:
        """Handle database connection logic."""
        obfuscated_url = str(make_url(url))

        save_to_env(obfuscated_url, url)

        result = await DatabaseConnection.test_connection(obfuscated_url)
        if result.connected:
            return obfuscated_url
        else:
            raise ConnectionError(f"Failed to connect to {url}: {result.message}")

    # Handle both single URL and list of URLs
    if isinstance(urls, str):
        return await save_connection(urls)
    else:
        return await asyncio.gather(*[save_connection(url) for url in urls])


# Caching Decorator
def cache(expire: int = None):
    """Async caching decorator using diskcache."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = (func.__qualname__, args, tuple(sorted(kwargs.items())))

            result = _cache.get(cache_key)
            if result is not None:
                return result

            result = await func(*args, **kwargs)
            _cache.set(cache_key, result, expire=expire)
            return result

        return wrapper

    return decorator
