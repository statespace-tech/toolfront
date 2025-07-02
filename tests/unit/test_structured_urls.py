"""Unit tests for structured URL types with selective masking."""

import pytest
from pydantic import SecretStr

from toolfront.models.url import APIURL, DatabaseURL


class TestDatabaseURL:
    """Test DatabaseURL masking and functionality."""

    def test_postgresql_url_masking(self):
        """Test PostgreSQL URL masks password but shows structure."""
        url = DatabaseURL.from_url_string("postgresql://user:secretpass@localhost:5432/mydb")

        assert str(url) == "postgresql://user:***@localhost:5432/mydb"
        assert url.to_display_string() == "postgresql://user:***@localhost:5432/mydb"
        assert url.to_connection_string() == "postgresql://user:secretpass@localhost:5432/mydb"

    def test_mysql_url_with_special_chars(self):
        """Test MySQL URL with special characters in password."""
        url = DatabaseURL.from_url_string("mysql://admin:p@ss$w0rd!@db.example.com:3306/prod")

        assert str(url) == "mysql://admin:***@db.example.com:3306/prod"
        assert url.to_connection_string() == "mysql://admin:p@ss$w0rd!@db.example.com:3306/prod"

    def test_snowflake_url_masking(self):
        """Test Snowflake URL structure preservation."""
        url = DatabaseURL.from_url_string("snowflake://user:pass@account.region.snowflakecomputing.com/db/schema")

        assert str(url) == "snowflake://user:***@account.region.snowflakecomputing.com/db/schema"
        assert url.to_connection_string() == "snowflake://user:pass@account.region.snowflakecomputing.com/db/schema"

    def test_sqlite_file_url_no_masking(self):
        """Test SQLite file URL remains unchanged (no password)."""
        url = DatabaseURL.from_url_string("sqlite:///path/to/database.db")

        assert str(url) == "sqlite:///path/to/database.db"
        assert url.to_connection_string() == "sqlite:///path/to/database.db"

    def test_url_without_password(self):
        """Test URL without password shows no masking."""
        url = DatabaseURL.from_url_string("postgresql://user@localhost:5432/mydb")

        assert str(url) == "postgresql://user@localhost:5432/mydb"
        assert url.to_connection_string() == "postgresql://user@localhost:5432/mydb"

    def test_url_without_username(self):
        """Test URL with only password (edge case)."""
        url = DatabaseURL.from_url_string("postgresql://:password@localhost:5432/mydb")

        assert str(url) == "postgresql://***@localhost:5432/mydb"
        assert url.to_connection_string() == "postgresql://:password@localhost:5432/mydb"

    def test_url_with_query_params(self):
        """Test URL with query parameters."""
        url = DatabaseURL.from_url_string("postgresql://user:pass@host:5432/db?sslmode=require&timeout=30")

        assert str(url) == "postgresql://user:***@host:5432/db?sslmode=require&timeout=30"
        assert url.to_connection_string() == "postgresql://user:pass@host:5432/db?sslmode=require&timeout=30"


class TestAPIURL:
    """Test APIURL masking and functionality."""

    def test_api_url_clean_display(self):
        """Test API URL shows only clean hostname in display."""
        url = APIURL.from_url_string(
            "https://api.polygon.io/v1/data", auth_query_params={"apikey": "secret123"}, query_params={"param": "value"}
        )

        # Display should show only clean URL
        assert str(url) == "https://api.polygon.io/v1/data"
        assert url.to_display_string() == "https://api.polygon.io/v1/data"

        # Connection should include all params with real secrets
        connection_str = url.to_connection_string()
        assert "apikey=secret123" in connection_str
        assert "param=value" in connection_str

    def test_api_url_with_port(self):
        """Test API URL with custom port."""
        url = APIURL.from_url_string(
            "https://api.example.com:8443/v2", auth_headers={"Authorization": "Bearer token123"}
        )

        assert str(url) == "https://api.example.com:8443/v2"
        assert url.to_connection_string() == "https://api.example.com:8443/v2"

        # Auth headers should be preserved separately
        auth_headers = url.get_auth_headers()
        assert auth_headers["Authorization"] == "Bearer token123"

    def test_api_url_with_auth_headers(self):
        """Test API URL with authentication headers."""
        url = APIURL.from_url_string(
            "https://api.example.com", auth_headers={"X-API-Key": "key123", "Authorization": "Bearer token456"}
        )

        # Display shows clean URL
        assert str(url) == "https://api.example.com"

        # Auth headers accessible with real values
        auth_headers = url.get_auth_headers()
        assert auth_headers["X-API-Key"] == "key123"
        assert auth_headers["Authorization"] == "Bearer token456"

    def test_api_url_mixed_auth(self):
        """Test API URL with both header and query auth."""
        url = APIURL.from_url_string(
            "https://api.example.com/data",
            auth_headers={"Authorization": "Bearer token123"},
            auth_query_params={"api_key": "key456"},
            query_params={"format": "json", "limit": "100"},
        )

        # Display shows only clean URL
        assert str(url) == "https://api.example.com/data"

        # Connection includes all query params
        connection_str = url.to_connection_string()
        assert "api_key=key456" in connection_str
        assert "format=json" in connection_str
        assert "limit=100" in connection_str

        # Auth headers preserved
        auth_headers = url.get_auth_headers()
        assert auth_headers["Authorization"] == "Bearer token123"


class TestURLResolution:
    """Test URL resolution functionality."""

    def test_database_url_display_matching(self):
        """Test that display strings can be matched back to original objects."""
        original_url = DatabaseURL.from_url_string("postgresql://user:secretpass@localhost:5432/mydb")
        display_str = str(original_url)

        # Simulate what resolution logic does
        assert display_str == "postgresql://user:***@localhost:5432/mydb"

        # In real resolution, we'd iterate through stored objects
        url_objects = [original_url]
        found_url = next((obj for obj in url_objects if str(obj) == display_str), None)

        assert found_url is not None
        assert found_url.to_connection_string() == "postgresql://user:secretpass@localhost:5432/mydb"

    def test_api_url_display_matching(self):
        """Test that API display strings can be matched back to original objects."""
        original_url = APIURL.from_url_string(
            "https://api.polygon.io/v1/data", auth_query_params={"apikey": "secret123"}
        )
        display_str = str(original_url)

        # Display should be clean
        assert display_str == "https://api.polygon.io/v1/data"

        # Resolution simulation
        url_objects = [original_url]
        found_url = next((obj for obj in url_objects if str(obj) == display_str), None)

        assert found_url is not None
        connection_str = found_url.to_connection_string()
        assert "apikey=secret123" in connection_str

    def test_multiple_urls_resolution(self):
        """Test resolution works with multiple URL objects."""
        db_url = DatabaseURL.from_url_string("postgresql://user:pass@localhost:5432/db")
        api_url = APIURL.from_url_string("https://api.polygon.io", auth_query_params={"apikey": "secret"})

        url_objects = [db_url, api_url]

        # Test database resolution
        db_display = str(db_url)
        found_db = next((obj for obj in url_objects if str(obj) == db_display), None)
        assert found_db is not None
        assert isinstance(found_db, DatabaseURL)
        assert found_db.to_connection_string() == "postgresql://user:pass@localhost:5432/db"

        # Test API resolution
        api_display = str(api_url)
        found_api = next((obj for obj in url_objects if str(obj) == api_display), None)
        assert found_api is not None
        assert isinstance(found_api, APIURL)
        assert "apikey=secret" in found_api.to_connection_string()


class TestSecretStrIntegration:
    """Test integration with pydantic SecretStr."""

    def test_database_password_is_secret_str(self):
        """Test that database passwords are stored as SecretStr."""
        url = DatabaseURL.from_url_string("postgresql://user:password@localhost:5432/db")

        assert isinstance(url.password, SecretStr)
        assert url.password.get_secret_value() == "password"

        # SecretStr should not leak in repr
        assert "password" not in repr(url.password)

    def test_api_auth_params_are_secret_str(self):
        """Test that API auth parameters are stored as SecretStr."""
        url = APIURL.from_url_string("https://api.example.com", auth_query_params={"apikey": "secret123"})

        assert "apikey" in url.auth_query_params
        assert isinstance(url.auth_query_params["apikey"], SecretStr)
        assert url.auth_query_params["apikey"].get_secret_value() == "secret123"

        # SecretStr should not leak in repr
        assert "secret123" not in repr(url.auth_query_params["apikey"])

    def test_url_object_equality(self):
        """Test that URL objects with same content are equal."""
        url1 = DatabaseURL.from_url_string("postgresql://user:pass@localhost:5432/db")
        url2 = DatabaseURL.from_url_string("postgresql://user:pass@localhost:5432/db")

        # Should be equal
        assert url1 == url2

        # Different URLs should not be equal
        url3 = DatabaseURL.from_url_string("postgresql://user:pass@localhost:5432/other_db")
        assert url1 != url3
