import importlib
import importlib.util
import logging
from urllib.parse import ParseResult, parse_qs, urlparse

from pydantic import BaseModel, Field
from sqlalchemy.engine.url import URL, make_url

from toolfront.models.api import API
from toolfront.models.database import ConnectionResult, Database
from toolfront.models.databases import DatabaseType, db_map
from toolfront.storage import load_connection, load_openapi_spec_from_clean_url, load_spec_url_from_clean_url

logger = logging.getLogger("toolfront.connection")


class Connection(BaseModel):
    """Connection to a data source."""

    async def connect(self) -> Database | API:
        """Connect to the data source."""
        raise NotImplementedError("Subclasses must implement connect")

    @classmethod
    async def test_connection(cls, url: str) -> ConnectionResult:
        """Test the connection to the data source."""
        try:
            connection = cls(url=url)
            connection = await connection.connect()
            return await connection.test_connection()
        except Exception as e:
            return ConnectionResult(connected=False, message=str(e))


class APIConnection(Connection):
    """API connection."""

    url: str = Field(..., description="Full API URL.")

    async def connect(self) -> API:
        # Get the clean URL (this is what we'll use for the API connection)
        clean_url = str(self.url)

        # Load OpenAPI spec from clean URL
        openapi_spec = load_openapi_spec_from_clean_url(clean_url)

        # Get the original spec URL that contains auth parameters
        original_spec_url = load_spec_url_from_clean_url(clean_url)
        if not original_spec_url:
            raise ConnectionError(f"No spec URL found for URL: {clean_url}")

        # Parse the original spec URL to extract auth parameters
        url: ParseResult = urlparse(original_spec_url)
        query_params = parse_qs(url.query)
        # Convert from lists to single values
        query_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}

        # Initialize auth containers
        auth_headers = {}
        auth_query_params = {}

        # Common auth parameter names
        auth_param_names = ["apikey", "api_key", "token", "access_token", "bearer", "key", "auth"]

        # Check OpenAPI spec for security schemes
        if openapi_spec and "components" in openapi_spec and "securitySchemes" in openapi_spec["components"]:
            for _scheme_name, scheme in openapi_spec["components"]["securitySchemes"].items():
                if scheme.get("type") == "apiKey":
                    param_name = scheme.get("name")
                    param_location = scheme.get("in", "query")

                    # Find matching parameter in query params (case-insensitive)
                    for qp_name, qp_value in list(query_params.items()):
                        if qp_name.lower() == param_name.lower():
                            if param_location == "header":
                                auth_headers[param_name] = qp_value
                                del query_params[qp_name]
                            elif param_location == "query":
                                auth_query_params[qp_name] = qp_value
                                del query_params[qp_name]
                            break
                elif scheme.get("type") == "http" and scheme.get("scheme") == "bearer":
                    # Look for bearer/token in query params
                    for qp_name, qp_value in list(query_params.items()):
                        if qp_name.lower() in ["bearer", "token", "access_token"]:
                            auth_headers["Authorization"] = f"Bearer {qp_value}"
                            del query_params[qp_name]
                            break
        else:
            # No spec or security schemes - use heuristics
            for qp_name, qp_value in list(query_params.items()):
                if qp_name.lower() in auth_param_names:
                    if qp_name.lower() in ["bearer", "token", "access_token"]:
                        auth_headers["Authorization"] = f"Bearer {qp_value}"
                        del query_params[qp_name]
                    else:
                        # Default to keeping in query params (like Polygon)
                        auth_query_params[qp_name] = qp_value
                        del query_params[qp_name]

        return API(
            url=clean_url, auth_headers=auth_headers, auth_query_params=auth_query_params, openapi_spec=openapi_spec
        )


class DatabaseConnection(Connection):
    url: str = Field(..., description="Full database URL.")

    async def connect(self) -> Database:
        # Load the actual connection URL and validate it
        url: URL = make_url(load_connection(self.url))

        drivername = url.drivername
        if drivername not in db_map:
            raise ValueError(f"Unsupported data source: {drivername}")

        db_type, db_class_name = db_map[drivername]

        # Set the correct async driver for certain databases
        if db_type == DatabaseType.MYSQL:
            if not importlib.util.find_spec("aiomysql"):
                raise ImportError("Missing dependencies for MySQL. Please install them using: uvx 'toolfront[mysql]'")
            url = url.set(drivername="mysql+aiomysql")
        elif db_type == DatabaseType.POSTGRESQL:
            if not importlib.util.find_spec("asyncpg"):
                raise ImportError(
                    "Missing dependencies for PostgreSQL. Please install them using: uvx 'toolfront[postgresql]'"
                )
            url = url.set(drivername=f"{drivername}+asyncpg")
        elif db_type == DatabaseType.SQLITE:
            if not importlib.util.find_spec("aiosqlite"):
                raise ImportError("Missing dependencies for SQLite. Please install them using: uvx 'toolfront[sqlite]'")
            url = url.set(drivername="sqlite+aiosqlite")
        elif db_type == DatabaseType.SQLSERVER:
            if not importlib.util.find_spec("pyodbc"):
                raise ImportError(
                    "Missing dependencies for SQLServer. Please install them using: uvx 'toolfront[sqlserver]'"
                )
            url = url.set(drivername="mssql+pyodbc")

        # Create and return the database instance
        module = importlib.import_module(f"toolfront.models.databases.{db_type.value}")
        db_class = getattr(module, db_class_name)
        return db_class(url=url)
