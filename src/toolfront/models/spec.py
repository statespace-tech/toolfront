import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx
import jsonref
import yaml
from pydantic import BaseModel, Field, field_validator

from toolfront.config import SPEC_DOWNLOAD_TTL


class Spec(BaseModel):
    """OpenAPI/Swagger specification with URL and spec content."""

    spec_config: dict = Field(..., description="The OpenAPI/Swagger specification content")
    spec_url: str = Field(..., description="The URL of the OpenAPI/Swagger specification")

    @field_validator("spec_config")
    def validate_spec(cls, v: dict) -> dict:
        """Validate the spec."""
        return jsonref.replace_refs(v)

    @property
    def url(self) -> str:
        """Get the base URL from the first server."""
        servers = self.get_servers()
        if not servers:
            raise ConnectionError("No servers found in OpenAPI/Swagger spec")

        server_url = servers[0].get("url")
        if not server_url:
            raise ConnectionError("No server URL found in OpenAPI/Swagger spec")

        return server_url

    @classmethod
    def from_spec_url(cls, spec_url: str) -> "Spec":
        """Load OpenAPI/Swagger spec from URL or filesystem."""
        from toolfront.cache import load_from_cache, save_to_cache

        if spec_url.startswith("file://"):
            # Handle file URL
            try:
                parsed_url = urlparse(spec_url)
                file_path = Path(parsed_url.path)

                if not file_path.exists():
                    raise ConnectionError(f"OpenAPI spec file not found: {file_path}")

                with file_path.open() as f:
                    config_spec = yaml.safe_load(f) if file_path.suffix.lower() in [".yaml", ".yml"] else json.load(f)

                spec = cls(spec_config=config_spec, spec_url=spec_url)
                save_to_cache(spec_url, spec.model_dump(), expire=SPEC_DOWNLOAD_TTL)
                return spec

            except Exception as e:
                raise ConnectionError(f"Failed to load OpenAPI/Swagger spec from {spec_url}: {e}")

        else:
            # Check if we have a cached download
            cached_spec = load_from_cache(spec_url)
            if cached_spec:
                return cls(**cached_spec)

            # Download and cache the spec
            try:
                with httpx.Client() as client:
                    response = client.get(spec_url)
                    response.raise_for_status()
                    spec_config = response.json()

                spec = cls(spec_config=spec_config, spec_url=spec_url)
                save_to_cache(spec_url, spec.model_dump(), expire=SPEC_DOWNLOAD_TTL)
                return spec

            except Exception as e:
                raise ConnectionError(f"Failed to load OpenAPI/Swagger spec from {spec_url}: {e}")

    def get_endpoint_spec(self, method: str, path: str) -> dict:
        """Get the endpoint spec from the spec."""
        endpoint_spec = self.spec_config.get("paths", {}).get(path, {}).get(method.lower(), {})
        if not endpoint_spec:
            raise RuntimeError(f"Endpoint not found: {method} {path}")
        return endpoint_spec

    def get_paths(self) -> dict:
        """Get the paths from the spec."""
        return self.spec_config.get("paths", {})

    def is_openapi(self) -> bool:
        """Check if this is an OpenAPI 3.x spec."""
        return "openapi" in self.spec_config

    def is_swagger(self) -> bool:
        """Check if this is a Swagger 2.x spec."""
        return "swagger" in self.spec_config

    def get_version(self) -> str:
        """Get the specification version."""
        if self.is_openapi():
            return self.spec_config.get("openapi", "3.0.0")
        elif self.is_swagger():
            return self.spec_config.get("swagger", "2.0")
        return "unknown"

    def get_servers(self) -> list[dict]:
        """Get servers from the spec (OpenAPI 3.x) or construct from host/basePath (Swagger 2.x)."""
        if self.is_openapi():
            return self.spec_config.get("servers", [])

        elif self.is_swagger():
            host = self.spec_config.get("host", "")
            base_path = self.spec_config.get("basePath", "")
            schemes = self.spec_config.get("schemes", ["https"])

            if host:
                return [{"url": f"{scheme}://{host}{base_path}"} for scheme in schemes]

        return []

    def get_security_schemes(self) -> dict:
        """Get security schemes from the spec."""
        if self.is_openapi():
            return self.spec_config.get("components", {}).get("securitySchemes", {})
        elif self.is_swagger():
            return self.spec_config.get("securityDefinitions", {})
        return {}

    def get_auth_headers_and_query_params(self) -> tuple[dict[str, str], dict[str, str]]:
        """Extract auth headers and query parameters from the original spec URL."""
        parsed_url = urlparse(self.spec_url)
        query_params = parse_qs(parsed_url.query)

        # Convert from lists to single values
        query_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}

        if not query_params:
            return {}, {}

        auth_headers = {}
        auth_query_params = {}

        # Try to match against security schemes if available
        security_schemes = self.get_security_schemes()

        for param_name, param_value in query_params.items():
            # Check if this parameter matches any security scheme
            matched = False
            for _, scheme in security_schemes.items():
                if scheme.get("type") == "apiKey" and scheme.get("name", "").lower() == param_name.lower():
                    if scheme.get("in") == "header":
                        auth_headers[scheme["name"]] = param_value
                    else:
                        auth_query_params[param_name] = param_value
                    matched = True
                    break

            # If no scheme match, use heuristics
            if not matched:
                param_lower = param_name.lower()
                if param_lower in ["bearer", "token", "access_token"]:
                    auth_headers["Authorization"] = f"Bearer {param_value}"
                elif param_lower in ["apikey", "api_key", "key", "auth"]:
                    auth_query_params[param_name] = param_value

        return auth_headers, auth_query_params
