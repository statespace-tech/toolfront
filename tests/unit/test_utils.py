"""Unit tests for utility functions in toolfront.utils."""

from toolfront.utils import sanitize_url


class TestSanitizeUrl:
    """Test cases for sanitize_url function."""

    def test_sanitize_url_with_password(self):
        """Test password removal from URLs."""
        url = "postgresql://user:password@localhost:5432/db"
        result = sanitize_url(url)
        assert result == "postgresql://user:***@localhost:5432/db"

    def test_sanitize_url_without_password(self):
        """Test URLs without passwords remain unchanged."""
        url = "postgresql://user@localhost:5432/db"
        result = sanitize_url(url)
        assert result == url

    def test_sanitize_url_no_auth(self):
        """Test URLs without authentication."""
        url = "postgresql://localhost:5432/db"
        result = sanitize_url(url)
        assert result == url

    def test_sanitize_file_url(self):
        """Test file URLs."""
        url = "file:///path/to/file.db"
        result = sanitize_url(url)
        assert result == url

    def test_sanitize_http_url_with_password(self):
        """Test HTTP URLs with authentication."""
        url = "https://user:secret@api.example.com/v1"
        result = sanitize_url(url)
        assert result == "https://user:***@api.example.com/v1"
