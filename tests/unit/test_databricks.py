"""Unit tests for Databricks integration logic."""

import pandas as pd
import pytest
from sqlalchemy.engine.url import make_url

from toolfront.models.databases.databricks import Databricks


def test_databricks_initialization():
    """Test that a Databricks instance can be created."""
    url = make_url("databricks://hostname:443/database?http_path=/path&token=token")
    db = Databricks(url=url)
    assert db.url.drivername == "databricks"
    assert db.url.host == "hostname"
    assert db.url.port == 443
    assert db.url.database == "database"
    assert db.url.query["http_path"] == "/path"
    assert db.url.query["token"] == "token"


def test_extract_token_from_query_parameter():
    """Test token extraction from URL query parameters."""
    url = make_url("databricks://hostname/db?http_path=/path&token=abc123")
    db = Databricks(url=url)
    assert db._extract_token() == "abc123"


def test_extract_token_from_username_password():
    """Test token extraction from username/password format."""
    url = make_url("databricks://token:abc123@hostname/db?http_path=/path")
    db = Databricks(url=url)
    assert db._extract_token() == "abc123"


def test_extract_token_from_access_token_parameter():
    """Test token extraction from access_token parameter."""
    url = make_url("databricks://hostname/db?http_path=/path&access_token=abc123")
    db = Databricks(url=url)
    assert db._extract_token() == "abc123"


def test_extract_token_from_personal_access_token_parameter():
    """Test token extraction from personal_access_token parameter."""
    url = make_url("databricks://hostname/db?http_path=/path&personal_access_token=abc123")
    db = Databricks(url=url)
    assert db._extract_token() == "abc123"


def test_extract_token_prioritizes_username_password():
    """Test that username/password format takes priority over query parameters."""
    url = make_url("databricks://token:abc123@hostname/db?http_path=/path&token=xyz789")
    db = Databricks(url=url)
    assert db._extract_token() == "abc123"


def test_extract_token_empty_when_missing():
    """Test that empty string is returned when no token is found."""
    url = make_url("databricks://hostname/db?http_path=/path")
    db = Databricks(url=url)
    assert db._extract_token() == ""


def test_format_table_names_standard_databricks():
    """Test table name formatting with standard Databricks columns."""
    data = pd.DataFrame({"database": ["catalog1", "catalog1", "catalog2"], "tableName": ["table1", "table2", "table3"]})
    url = make_url("databricks://hostname/db")
    db = Databricks(url=url)

    result = db._format_table_names(data)
    expected = ["catalog1.table1", "catalog1.table2", "catalog2.table3"]
    assert result == expected


def test_format_table_names_alternative_databricks():
    """Test table name formatting with alternative Databricks columns."""
    data = pd.DataFrame(
        {"databaseName": ["catalog1", "catalog1", "catalog2"], "tableName": ["table1", "table2", "table3"]}
    )
    url = make_url("databricks://hostname/db")
    db = Databricks(url=url)

    result = db._format_table_names(data)
    expected = ["catalog1.table1", "catalog1.table2", "catalog2.table3"]
    assert result == expected


def test_format_table_names_fallback_two_columns():
    """Test table name formatting fallback with two columns."""
    data = pd.DataFrame({0: ["schema1", "schema1", "schema2"], 1: ["table1", "table2", "table3"]})
    url = make_url("databricks://hostname/db")
    db = Databricks(url=url)

    result = db._format_table_names(data)
    expected = ["schema1.table1", "schema1.table2", "schema2.table3"]
    assert result == expected


def test_format_table_names_single_column():
    """Test table name formatting with single column."""
    data = pd.DataFrame({0: ["table1", "table2", "table3"]})
    url = make_url("databricks://hostname/db")
    db = Databricks(url=url)

    result = db._format_table_names(data)
    expected = ["table1", "table2", "table3"]
    assert result == expected


def test_format_table_names_empty_dataframe():
    """Test table name formatting with empty DataFrame."""
    data = pd.DataFrame()
    url = make_url("databricks://hostname/db")
    db = Databricks(url=url)

    result = db._format_table_names(data)
    assert result == []


def test_get_detailed_table_info_query():
    """Test SQL query generation for detailed table info."""
    url = make_url("databricks://hostname/db")
    db = Databricks(url=url)

    query = db._get_detailed_table_info("catalog1", "schema1", "table1")

    assert "catalog1.information_schema.columns" in query
    assert "table_schema = 'schema1'" in query
    assert "table_name = 'table1'" in query
    assert "column_name" in query
    assert "data_type" in query
    assert "is_nullable" in query
    assert "column_default" in query
    assert "ordinal_position" in query
    assert "ORDER BY ordinal_position" in query


@pytest.mark.asyncio
async def test_inspect_table_path_validation():
    """Test table path validation logic."""
    url = make_url("databricks://hostname/db")
    db = Databricks(url=url)

    # Test empty path
    with pytest.raises(ValueError, match="Invalid table path"):
        await db.inspect_table("")

    # Test invalid format
    with pytest.raises(Exception, match="Invalid table path.*Expected format"):
        await db.inspect_table("single_name")


@pytest.mark.asyncio
async def test_sample_table_path_validation():
    """Test sample table path validation logic."""
    url = make_url("databricks://hostname/db")
    db = Databricks(url=url)

    # Test empty path
    with pytest.raises(ValueError, match="Invalid table path"):
        await db.sample_table("")

    # Test non-string path
    with pytest.raises(ValueError, match="Invalid table path"):
        await db.sample_table(None)
