"""Unit tests for model validation logic in toolfront.models."""

from toolfront.models.database import Table


class TestTable:
    """Test cases for Table model."""

    def test_simple_table_name(self):
        """Test creating table with simple name."""
        table = Table(path="users")
        assert table.path == "users"

    def test_schema_qualified_table(self):
        """Test creating table with schema."""
        table = Table(path="public.users")
        assert table.path == "public.users"

    def test_fully_qualified_table(self):
        """Test creating table with database.schema.table format."""
        table = Table(path="mydb.public.users")
        assert table.path == "mydb.public.users"

    def test_table_field_description(self):
        """Test that field description is set correctly."""
        field = Table.model_fields["path"]
        assert "Full table path in dot notation" in field.description
