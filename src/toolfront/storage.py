"""
Connection storage and caching utilities.
"""

import logging
from urllib.parse import urlparse

import diskcache
import httpx
import jsonref
from sqlalchemy.engine.url import make_url

logger = logging.getLogger("toolfront")
_cache = diskcache.Cache(".toolfront_cache")


def _get_or_download_openapi_spec(spec_url: str) -> dict | None:
    """Get OpenAPI spec from cache or download if not cached."""
    # Check cache first
    cached_spec = load_openapi_spec_config(spec_url)
    if cached_spec is not None:
        logger.debug(f"Using cached OpenAPI spec for {spec_url}")
        return cached_spec

    # Download if not cached
    try:
        logger.debug(f"Downloading OpenAPI spec from {spec_url}")
        with httpx.Client() as client:
            response = client.get(spec_url)
            response.raise_for_status()
            spec = response.json()
            parsed_spec = jsonref.replace_refs(spec)

            # Cache the downloaded spec
            save_openapi_spec_config(spec_url, parsed_spec)
            logger.info(f"Successfully downloaded and cached OpenAPI spec from {spec_url}")
            return parsed_spec
    except Exception as e:
        logger.warning(f"Failed to download OpenAPI spec from {spec_url}: {e}")
        return None


async def save_connection(url: str) -> str:
    """Save a connection to the cache."""
    if url.startswith("http"):
        # Handle OpenAPI spec URLs
        from toolfront.models.connection import APIConnection

        parsed = urlparse(url)
        openapi_spec = _get_or_download_openapi_spec(url)

        if openapi_spec is None:
            raise ConnectionError(f"Failed to download OpenAPI spec from {url}")

        # Extract base URL from OpenAPI spec
        base_url = openapi_spec.get("servers", [])[0].get("url", None) if openapi_spec else None
        if base_url is None:
            raise ConnectionError("No servers found in OpenAPI spec")

        # Create clean URL (netloc + base_url from spec)
        clean_url = f"{parsed.scheme}://{parsed.netloc}{base_url if base_url.startswith('/') else ''}"

        # Store mapping: Clean URL -> OpenAPI spec URL
        # (OpenAPI spec dict is already cached by _get_or_download_openapi_spec)
        save_clean_url_to_spec_url_mapping(clean_url, url)

        result = await APIConnection.test_connection(clean_url)

        if result.connected:
            logger.info(f"Successfully connected to {clean_url}")
            return clean_url
        else:
            logger.error(f"Failed to connect to {url}: {result.message}")
            raise ConnectionError(f"Failed to connect to {url}: {result.message}")
    else:
        # Handle database URLs
        from toolfront.models.connection import DatabaseConnection

        parsed = make_url(url)

        # Create obfuscated version (make_url automatically obfuscates passwords)
        obfuscated_url = str(parsed)

        # Store mapping: obfuscated URL -> full URL
        save_obfuscated_to_full_url_mapping(obfuscated_url, url)

        result = await DatabaseConnection.test_connection(obfuscated_url)

        if result.connected:
            logger.info(f"Successfully connected to {obfuscated_url}")
            return obfuscated_url
        else:
            logger.error(f"Failed to connect to {url}: {result.message}")
            raise ConnectionError(f"Failed to connect to {url}: {result.message}")


def save_clean_url_to_spec_url_mapping(clean_url: str, spec_url: str) -> None:
    """Save mapping from clean URL to OpenAPI spec URL."""
    _cache.set(key=f"clean_to_spec:{clean_url}", value=spec_url)


def save_openapi_spec_config(spec_url: str, spec_config: dict) -> None:
    """Save OpenAPI spec config to cache."""
    _cache.set(key=f"spec_config:{spec_url}", value=spec_config)


def save_obfuscated_to_full_url_mapping(obfuscated_url: str, full_url: str) -> None:
    """Save mapping from obfuscated database URL to full URL."""
    _cache.set(key=f"obfuscated_to_full:{obfuscated_url}", value=full_url)


def load_connection(url: str) -> str:
    """Load a connection from the cache - returns the original URL if it's a clean/obfuscated URL."""
    if url.startswith("http"):
        # For HTTP URLs, check if it's a clean URL and get the original spec URL
        spec_url = load_spec_url_from_clean_url(url)
        return spec_url if spec_url else url
    else:
        # For database URLs, check if it's obfuscated and get the full URL
        full_url = load_full_url_from_obfuscated(url)
        return full_url if full_url else url


def load_spec_url_from_clean_url(clean_url: str) -> str | None:
    """Load OpenAPI spec URL from clean URL."""
    return _cache.get(key=f"clean_to_spec:{clean_url}", default=None)


def load_openapi_spec_config(spec_url: str) -> dict | None:
    """Load OpenAPI spec config from cache."""
    return _cache.get(key=f"spec_config:{spec_url}", default=None)


def load_full_url_from_obfuscated(obfuscated_url: str) -> str | None:
    """Load full database URL from obfuscated URL."""
    return _cache.get(key=f"obfuscated_to_full:{obfuscated_url}", default=None)


def load_openapi_spec_from_clean_url(clean_url: str) -> dict | None:
    """Load OpenAPI spec config from clean URL (convenience function)."""
    spec_url = load_spec_url_from_clean_url(clean_url)
    if spec_url:
        return load_openapi_spec_config(spec_url)
    return None


def clear_cache() -> None:
    """Clear all cached data."""
    _cache.clear()
