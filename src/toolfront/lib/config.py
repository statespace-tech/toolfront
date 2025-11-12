"""Shared config reader for toolfront CLI - reads from dev-tools config.toml"""

import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older Python


def get_config_path() -> Path:
    """Get the config file path (cross-platform)"""
    if sys.platform == "darwin":
        # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "toolfront"
    elif sys.platform == "win32":
        # Windows
        config_dir = Path.home() / "AppData" / "Roaming" / "toolfront"
    else:
        # Linux/Unix
        config_dir = Path.home() / ".config" / "toolfront"

    return config_dir / "config.toml"


def load_config() -> dict:
    """Load config from TOML file"""
    config_path = get_config_path()

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found at {config_path}\n"
            f"Run 'dev-tools setup --save' to create it, or set TOOLFRONT_API_KEY and TOOLFRONT_GATEWAY_URL env vars."
        )

    with open(config_path, "rb") as f:
        return tomllib.load(f)


def get_current_context() -> dict:
    """Get the current context configuration"""
    config = load_config()
    current_context_name = config.get("current_context")

    if not current_context_name:
        raise ValueError("No current_context set in config file")

    contexts = config.get("contexts", {})
    context = contexts.get(current_context_name)

    if not context:
        raise ValueError(f"Context '{current_context_name}' not found in config")

    return context


def get_api_credentials(api_key: str | None = None, gateway_url: str | None = None) -> tuple[str, str]:
    """
    Get API credentials, preferring explicit args, then config file, then env vars.

    Returns: (gateway_url, api_key)
    """
    import os

    # If both are provided explicitly, use them
    if api_key and gateway_url:
        return gateway_url, api_key

    # Try to load from config file
    try:
        context = get_current_context()
        config_gateway_url = context.get("api_url")
        config_api_key = context.get("api_key")

        # Use config values, but allow CLI args to override
        final_gateway_url = gateway_url or config_gateway_url
        final_api_key = api_key or config_api_key

        if final_gateway_url and final_api_key:
            return final_gateway_url, final_api_key

    except (FileNotFoundError, ValueError):
        # Config file doesn't exist or is invalid, fall back to env vars
        pass

    # Fall back to environment variables
    final_gateway_url = gateway_url or os.getenv("TOOLFRONT_GATEWAY_URL", "https://api.toolfront.ai")
    final_api_key = api_key or os.getenv("TOOLFRONT_API_KEY")

    if not final_api_key:
        raise ValueError(
            "API key not found. Either:\n"
            "1. Run 'dev-tools setup --save' to configure context\n"
            "2. Use --api-key flag\n"
            "3. Set TOOLFRONT_API_KEY environment variable"
        )

    return final_gateway_url, final_api_key
