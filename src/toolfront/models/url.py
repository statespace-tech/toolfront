"""Structured URL types with selective SecretStr masking."""

from urllib.parse import parse_qs, urlparse, urlunparse

from pydantic import BaseModel, Field, SecretStr


class DatabaseURL(BaseModel):
    """Database URL with structured secret handling."""

    scheme: str = Field(..., description="Database scheme (postgresql, mysql, etc.)")
    username: str | None = Field(None, description="Database username")
    password: SecretStr | None = Field(None, description="Database password")
    hostname: str = Field(..., description="Database hostname")
    port: int | None = Field(None, description="Database port")
    database: str | None = Field(None, description="Database name")
    query_params: dict[str, str] = Field(default_factory=dict, description="Additional query parameters")

    @classmethod
    def from_url_string(cls, url: str) -> "DatabaseURL":
        """Parse a database URL string into structured components."""
        parsed = urlparse(url)

        # Parse query parameters
        query_params = {}
        if parsed.query:
            query_dict = parse_qs(parsed.query)
            query_params = {k: v[0] if len(v) == 1 else v for k, v in query_dict.items()}

        # Handle file-based databases (SQLite, DuckDB)
        if parsed.scheme in ("sqlite", "duckdb"):
            return cls(
                scheme=parsed.scheme,
                username=parsed.username,
                password=SecretStr(parsed.password) if parsed.password else None,
                hostname=parsed.hostname or "",
                port=parsed.port,
                database=parsed.path,  # Keep full path for file databases
                query_params=query_params,
            )
        else:
            return cls(
                scheme=parsed.scheme,
                username=parsed.username,
                password=SecretStr(parsed.password) if parsed.password else None,
                hostname=parsed.hostname or "",
                port=parsed.port,
                database=parsed.path.lstrip("/") if parsed.path else None,
                query_params=query_params,
            )

    def to_connection_string(self) -> str:
        """Generate the full connection string for actual database connections."""
        # Handle file-based databases differently
        if self.scheme in ("sqlite", "duckdb"):
            # Build query string
            query = ""
            if self.query_params:
                query_parts = [f"{k}={v}" for k, v in self.query_params.items()]
                query = "&".join(query_parts)

            # For file databases, manually construct to preserve slashes
            path = self.database or ""
            # If path starts with /, add extra slash for absolute paths
            url = f"{self.scheme}://{path}" if path.startswith("/") else f"{self.scheme}:{path}"
            if query:
                url += f"?{query}"
            return url

        # Regular database connection string
        # Build netloc
        netloc = ""
        if self.username or self.password:
            if self.username:  # Non-empty username
                netloc = self.username
                if self.password:
                    netloc += f":{self.password.get_secret_value()}"
            elif self.password:  # Password without username
                netloc = f":{self.password.get_secret_value()}"
            netloc += "@"

        netloc += self.hostname
        if self.port:
            netloc += f":{self.port}"

        # Build path
        path = ""
        if self.database:
            path = f"/{self.database}"

        # Build query string
        query = ""
        if self.query_params:
            query_parts = [f"{k}={v}" for k, v in self.query_params.items()]
            query = "&".join(query_parts)

        return urlunparse((self.scheme, netloc, path, "", query, ""))

    def to_display_string(self) -> str:
        """Generate a display string with masked password."""
        # Handle file-based databases differently
        if self.scheme in ("sqlite", "duckdb"):
            # For file databases, just return as-is (no passwords to mask)
            query = ""
            if self.query_params:
                query_parts = [f"{k}={v}" for k, v in self.query_params.items()]
                query = "&".join(query_parts)

            # Manually construct to preserve slashes
            path = self.database or ""
            # If path starts with /, add extra slash for absolute paths
            url = f"{self.scheme}://{path}" if path.startswith("/") else f"{self.scheme}:{path}"
            if query:
                url += f"?{query}"
            return url

        # Regular database display string with masked password
        # Build netloc with masked password
        netloc = ""
        if self.username or self.password:
            if self.username:  # Non-empty username
                netloc = self.username
                if self.password:
                    netloc += ":***"
            elif self.password:  # Password without username
                netloc = "***"
            netloc += "@"

        netloc += self.hostname
        if self.port:
            netloc += f":{self.port}"

        # Build path
        path = ""
        if self.database:
            path = f"/{self.database}"

        # Build query string (don't mask query params for databases)
        query = ""
        if self.query_params:
            query_parts = [f"{k}={v}" for k, v in self.query_params.items()]
            query = "&".join(query_parts)

        return urlunparse((self.scheme, netloc, path, "", query, ""))

    def __str__(self) -> str:
        """String representation shows display version."""
        return self.to_display_string()

    def matches_display_string(self, display_str: str) -> bool:
        """Check if this URL object matches a display string."""
        our_display = self.to_display_string()
        if our_display == display_str:
            return True

        # Also check if the display_str is the same as our display but with *** replaced by the actual password
        # This handles the case where tools receive a masked URL and parse it literally
        if "***" in our_display:
            # Create a version without password for comparison
            parsed = urlparse(display_str)
            our_parsed = urlparse(our_display)

            # Compare everything except the password
            return (
                parsed.scheme == our_parsed.scheme
                and parsed.username == our_parsed.username
                and parsed.hostname == our_parsed.hostname
                and parsed.port == our_parsed.port
                and parsed.path == our_parsed.path
                and parsed.query == our_parsed.query
            )

        return False


class APIURL(BaseModel):
    """API URL with structured secret handling."""

    scheme: str = Field(..., description="URL scheme (http, https)")
    hostname: str = Field(..., description="API hostname")
    path: str = Field(default="", description="API path")
    port: int | None = Field(None, description="API port")
    auth_headers: dict[str, SecretStr] = Field(default_factory=dict, description="Authentication headers")
    auth_query_params: dict[str, SecretStr] = Field(default_factory=dict, description="Authentication query parameters")
    query_params: dict[str, str] = Field(default_factory=dict, description="Non-auth query parameters")

    @classmethod
    def from_url_string(
        cls,
        url: str,
        auth_headers: dict[str, str] | None = None,
        auth_query_params: dict[str, str] | None = None,
        query_params: dict[str, str] | None = None,
    ) -> "APIURL":
        """Parse an API URL string into structured components."""
        parsed = urlparse(url)

        # Convert auth parameters to SecretStr
        auth_headers_secret = {}
        if auth_headers:
            auth_headers_secret = {k: SecretStr(v) for k, v in auth_headers.items()}

        auth_query_secret = {}
        if auth_query_params:
            auth_query_secret = {k: SecretStr(v) for k, v in auth_query_params.items()}

        return cls(
            scheme=parsed.scheme,
            hostname=parsed.hostname or "",
            path=parsed.path,
            port=parsed.port,
            auth_headers=auth_headers_secret,
            auth_query_params=auth_query_secret,
            query_params=query_params or {},
        )

    def to_connection_string(self) -> str:
        """Generate the full URL for actual API connections."""
        # Build netloc
        netloc = self.hostname
        if self.port:
            netloc += f":{self.port}"

        # Combine all query params (auth and non-auth)
        all_query_params = {}
        all_query_params.update(self.query_params)
        # Add auth query params with actual values
        for k, secret_v in self.auth_query_params.items():
            all_query_params[k] = secret_v.get_secret_value()

        # Build query string
        query = ""
        if all_query_params:
            query_parts = [f"{k}={v}" for k, v in all_query_params.items()]
            query = "&".join(query_parts)

        return urlunparse((self.scheme, netloc, self.path, "", query, ""))

    def to_display_string(self) -> str:
        """Generate a clean display string showing only the hostname and path."""
        # Build netloc
        netloc = self.hostname
        if self.port:
            netloc += f":{self.port}"

        # Show only clean URL without any query parameters
        return urlunparse((self.scheme, netloc, self.path, "", "", ""))

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers with actual secret values."""
        return {k: v.get_secret_value() for k, v in self.auth_headers.items()}

    def __str__(self) -> str:
        """String representation shows display version."""
        return self.to_display_string()

    def matches_display_string(self, display_str: str) -> bool:
        """Check if this URL object matches a display string."""
        our_display = self.to_display_string()
        if our_display == display_str:
            return True

        # For API URLs, also match if they have the same base structure
        # (since API URLs don't typically have *** in display strings)
        parsed = urlparse(display_str)
        our_parsed = urlparse(our_display)

        return (
            parsed.scheme == our_parsed.scheme
            and parsed.hostname == our_parsed.hostname
            and parsed.port == our_parsed.port
            and parsed.path == our_parsed.path
        )
