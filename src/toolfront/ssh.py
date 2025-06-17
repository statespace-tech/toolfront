"""
SSH tunnel management for secure database connections.
"""

import logging
import socket
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

from sshtunnel import SSHTunnelForwarder

logger = logging.getLogger("toolfront.ssh")


@dataclass
class SSHConfig:
    """SSH tunnel configuration."""

    ssh_host: str
    ssh_port: int = 22
    ssh_user: str | None = None
    ssh_password: str | None = None
    ssh_key_path: str | None = None
    remote_host: str = "localhost"
    remote_port: int = 5432
    local_port: int | None = None


class SSHTunnelManager:
    """Manages SSH tunnels for database connections."""

    def __init__(self, config: SSHConfig):
        self.config = config
        self._tunnel_forwarder: SSHTunnelForwarder | None = None
        self.local_port: int | None = None

    def _find_free_port(self) -> int:
        """Find a free local port for the tunnel."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", 0))
            return s.getsockname()[1]

    def _get_ssh_key_path(self) -> str | None:
        """Get the SSH key path, expanding user home directory if needed."""
        if not self.config.ssh_key_path:
            return None

        path = Path(self.config.ssh_key_path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"SSH key file not found: {path}")

        return str(path)

    @asynccontextmanager
    async def tunnel(self) -> AsyncIterator[int]:
        """Context manager for SSH tunnel lifecycle.

        Returns:
            The local port number for the tunnel.
        """
        if self._tunnel_forwarder is not None:
            raise RuntimeError("Tunnel is already active")

        # Determine local port
        local_port = self.config.local_port or self._find_free_port()

        # Prepare SSH authentication
        ssh_pkey = self._get_ssh_key_path()

        # Create tunnel configuration
        tunnel_kwargs = {
            "ssh_address_or_host": (self.config.ssh_host, self.config.ssh_port),
            "ssh_username": self.config.ssh_user,
            "remote_bind_address": (self.config.remote_host, self.config.remote_port),
            "local_bind_address": ("localhost", local_port),
        }

        # Add authentication
        if ssh_pkey:
            tunnel_kwargs["ssh_pkey"] = ssh_pkey
        if self.config.ssh_password:
            tunnel_kwargs["ssh_password"] = self.config.ssh_password

        logger.info(
            f"Creating SSH tunnel: {self.config.ssh_host}:{self.config.ssh_port} -> "
            f"localhost:{local_port} -> {self.config.remote_host}:{self.config.remote_port}"
        )

        # Create and start tunnel
        self._tunnel_forwarder = SSHTunnelForwarder(**tunnel_kwargs)

        try:
            self._tunnel_forwarder.start()
            self.local_port = self._tunnel_forwarder.local_bind_port
            logger.info(f"SSH tunnel established on localhost:{self.local_port}")
            yield self.local_port
        except Exception as e:
            logger.error(f"Failed to establish SSH tunnel: {e}")
            raise
        finally:
            if self._tunnel_forwarder:
                logger.info("Closing SSH tunnel")
                self._tunnel_forwarder.stop()
                self._tunnel_forwarder = None
                self.local_port = None

    def is_active(self) -> bool:
        """Check if the tunnel is currently active."""
        return self._tunnel_forwarder is not None and self._tunnel_forwarder.is_active


def parse_ssh_params(url_params: dict[str, str]) -> SSHConfig | None:
    """Parse SSH parameters from URL query parameters.

    Args:
        url_params: Dictionary of URL query parameters

    Returns:
        SSHConfig if SSH parameters are present, None otherwise
    """
    ssh_host = url_params.get("ssh_host")
    if not ssh_host:
        return None

    ssh_port = int(url_params.get("ssh_port", "22"))
    ssh_user = url_params.get("ssh_user")
    ssh_password = url_params.get("ssh_password")
    ssh_key_path = url_params.get("ssh_key_path")

    # Validate that we have some form of authentication
    if not ssh_user:
        raise ValueError("ssh_user is required for SSH tunnel")

    if not ssh_password and not ssh_key_path:
        raise ValueError("Either ssh_password or ssh_key_path is required for SSH tunnel")

    return SSHConfig(
        ssh_host=ssh_host,
        ssh_port=ssh_port,
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        ssh_key_path=ssh_key_path,
    )


def extract_ssh_params(url: str) -> tuple[str, SSHConfig | None]:
    """Extract SSH parameters from a database URL.

    Args:
        url: Database URL potentially containing SSH parameters

    Returns:
        Tuple of (clean_url_without_ssh_params, ssh_config_or_none)
    """
    from urllib.parse import parse_qs, urlparse, urlunparse

    parsed = urlparse(url)
    query_params = parse_qs(parsed.query, keep_blank_values=True)

    # Convert query params to single values (parse_qs returns lists)
    flat_params = {k: v[0] if v else "" for k, v in query_params.items()}

    # Extract SSH config
    ssh_config = parse_ssh_params(flat_params)

    if ssh_config:
        # Remove SSH parameters from URL
        non_ssh_params = {k: v for k, v in query_params.items() if not k.startswith("ssh_")}

        # Rebuild query string
        new_query = "&".join(f"{k}={v[0]}" for k, v in non_ssh_params.items()) if non_ssh_params else ""

        # Rebuild URL without SSH parameters
        clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

        # Update SSH config with database connection details
        ssh_config.remote_host = parsed.hostname or "localhost"
        ssh_config.remote_port = parsed.port or (5432 if parsed.scheme == "postgresql" else 3306)

        return clean_url, ssh_config

    return url, None
