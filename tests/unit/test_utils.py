"""Unit tests for utility functions."""

from datetime import datetime

import pandas as pd

from toolfront.config import MAX_DATA_ROWS
from toolfront.utils import mask_database_password, serialize_dataframe, serialize_response, tokenize


class TestMaskDatabasePassword:
    """Test the mask_database_password utility function."""

    def test_basic_postgresql_url(self):
        url = "postgresql://user:password@localhost:5432/mydb"
        result = mask_database_password(url)
        assert result == "postgresql://user:***@localhost:5432/mydb"

    def test_mysql_url_with_domain(self):
        url = "mysql://admin:secret123@db.example.com/prod"
        result = mask_database_password(url)
        assert result == "mysql://admin:***@db.example.com/prod"

    def test_url_with_special_chars_in_password(self):
        url = "postgresql://postgres:my$ecretP@ss@host.com:5432/database"
        result = mask_database_password(url)
        assert result == "postgresql://postgres:***@host.com:5432/database"

    def test_sqlite_file_url_no_password(self):
        url = "sqlite:///path/to/database.db"
        result = mask_database_password(url)
        assert result == "sqlite:///path/to/database.db"  # Unchanged

    def test_duckdb_file_url_no_password(self):
        url = "duckdb:///home/user/data.duckdb"
        result = mask_database_password(url)
        assert result == "duckdb:///home/user/data.duckdb"  # Unchanged

    def test_snowflake_url(self):
        url = "snowflake://user:pass@account.region.snowflakecomputing.com/db/schema"
        result = mask_database_password(url)
        assert result == "snowflake://user:***@account.region.snowflakecomputing.com/db/schema"

    def test_sqlserver_with_query_params(self):
        url = "mssql://sa:P@ssw0rd!@server:1433/database?driver=ODBC+Driver+17+for+SQL+Server"
        result = mask_database_password(url)
        assert result == "mssql://sa:***@server:1433/database?driver=ODBC+Driver+17+for+SQL+Server"

    def test_url_without_username(self):
        url = "postgresql://:password@localhost:5432/mydb"
        result = mask_database_password(url)
        assert result == "postgresql://***@localhost:5432/mydb"

    def test_url_without_port(self):
        url = "postgresql://user:password@localhost/mydb"
        result = mask_database_password(url)
        assert result == "postgresql://user:***@localhost/mydb"

    def test_url_with_fragment(self):
        url = "postgresql://user:password@localhost:5432/mydb#fragment"
        result = mask_database_password(url)
        assert result == "postgresql://user:***@localhost:5432/mydb#fragment"

    def test_empty_password(self):
        url = "postgresql://user:@localhost:5432/mydb"
        result = mask_database_password(url)
        # Empty password is still considered a password
        assert result == "postgresql://user:***@localhost:5432/mydb"

    def test_url_with_encoded_chars(self):
        url = "postgresql://user:p%40ssw%3Drd@localhost:5432/mydb"
        result = mask_database_password(url)
        assert result == "postgresql://user:***@localhost:5432/mydb"

    def test_bigquery_url(self):
        url = "bigquery://project-id/dataset"
        result = mask_database_password(url)
        assert result == "bigquery://project-id/dataset"  # No password to mask

    def test_databricks_url_with_token(self):
        # Databricks typically uses tokens in connection params, not in URL
        url = "databricks://token:dapi1234567890@host.databricks.com:443/http_path"
        result = mask_database_password(url)
        assert result == "databricks://token:***@host.databricks.com:443/http_path"


class TestTokenize:
    """Test the tokenize utility function."""

    def test_simple_word(self):
        result = tokenize("users")
        assert result == ["users"]

    def test_underscore_separation(self):
        result = tokenize("user_profiles")
        assert result == ["user", "profiles"]

    def test_dash_separation(self):
        result = tokenize("user-profiles")
        assert result == ["user", "profiles"]

    def test_dot_separation(self):
        result = tokenize("user.profiles")
        assert result == ["user", "profiles"]

    def test_slash_separation(self):
        result = tokenize("user/profiles")
        assert result == ["user", "profiles"]

    def test_mixed_separators(self):
        result = tokenize("user_profile-data.old/backup")
        assert result == ["user", "profile", "data", "old", "backup"]

    def test_multiple_consecutive_separators(self):
        result = tokenize("user__profile--data")
        assert result == ["user", "profile", "data"]

    def test_empty_string(self):
        result = tokenize("")
        assert result == []

    def test_only_separators(self):
        result = tokenize("___---...")
        assert result == []

    def test_case_conversion(self):
        result = tokenize("USER_PROFILES")
        assert result == ["user", "profiles"]

    def test_mixed_case(self):
        result = tokenize("User_Profile_Data")
        assert result == ["user", "profile", "data"]

    def test_leading_trailing_separators(self):
        result = tokenize("_user_profiles_")
        assert result == ["user", "profiles"]

    def test_single_character_tokens(self):
        result = tokenize("a_b_c")
        assert result == ["a", "b", "c"]


class TestSerializeResponse:
    """Test the generic serialize_response function."""

    def test_dataframe_input(self, sample_dataframe):
        result = serialize_response(sample_dataframe)
        # Should delegate to serialize_dataframe
        assert "data" in result
        assert "row_count" in result
        assert result["data"]["type"] == "table"

    def test_string_input(self):
        result = serialize_response("hello world")
        assert result == {"data": "hello world", "type": "str"}

    def test_integer_input(self):
        result = serialize_response(42)
        assert result == {"data": 42, "type": "int"}

    def test_list_input(self):
        result = serialize_response([1, 2, 3])
        assert result == {"data": [1, 2, 3], "type": "list"}

    def test_dict_input(self):
        data = {"key": "value"}
        result = serialize_response(data)
        assert result == {"data": data, "type": "dict"}

    def test_none_input(self):
        result = serialize_response(None)
        assert result == {"data": None, "type": "NoneType"}


class TestSerializeDataFrame:
    """Test DataFrame serialization functionality."""

    def test_basic_dataframe_serialization(self, sample_dataframe):
        result = serialize_dataframe(sample_dataframe)

        assert "data" in result
        assert "row_count" in result
        assert result["row_count"] == 4

        table_data = result["data"]
        assert table_data["type"] == "table"
        assert "columns" in table_data
        assert "rows" in table_data
        assert table_data["columns"] == ["index", "id", "name", "value", "active"]

    def test_dataframe_with_none_values(self):
        df = pd.DataFrame({"col1": [1, None, 3], "col2": ["a", "b", None]})
        result = serialize_dataframe(df)

        # Check that None values are properly serialized
        rows = result["data"]["rows"]
        assert rows[1][1] is None  # None in col1
        assert rows[2][2] is None  # None in col2

    def test_dataframe_with_datetime(self):
        df = pd.DataFrame(
            {"timestamp": [datetime(2023, 1, 1, 12, 0, 0), datetime(2023, 1, 2, 13, 0, 0)], "value": [10, 20]}
        )
        result = serialize_dataframe(df)

        rows = result["data"]["rows"]
        # Check that datetime is converted to ISO format
        assert rows[0][1] == "2023-01-01T12:00:00"
        assert rows[1][1] == "2023-01-02T13:00:00"

    def test_dataframe_with_pandas_timestamp(self):
        df = pd.DataFrame({"timestamp": pd.to_datetime(["2023-01-01", "2023-01-02"]), "value": [10, 20]})
        result = serialize_dataframe(df)

        rows = result["data"]["rows"]
        # Should serialize pandas Timestamp objects
        assert "2023-01-01" in rows[0][1]
        assert "2023-01-02" in rows[1][1]

    def test_dataframe_with_period(self):
        df = pd.DataFrame({"period": pd.period_range("2023-01", periods=2, freq="M"), "value": [10, 20]})
        result = serialize_dataframe(df)

        # Period objects should be converted to ISO format
        rows = result["data"]["rows"]
        assert "2023-01" in rows[0][1] or "2023-02" in rows[0][1]

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        result = serialize_dataframe(df)

        assert result["row_count"] == 0
        assert result["data"]["rows"] == []
        assert result["data"]["columns"] == ["index"]

    def test_dataframe_truncation(self):
        # Create a DataFrame larger than MAX_DATA_ROWS
        large_df = pd.DataFrame(
            {"col1": range(MAX_DATA_ROWS + 10), "col2": [f"value_{i}" for i in range(MAX_DATA_ROWS + 10)]}
        )
        result = serialize_dataframe(large_df)

        assert result["row_count"] == MAX_DATA_ROWS + 10
        assert len(result["data"]["rows"]) == MAX_DATA_ROWS
        assert "message" in result
        assert "truncated" in result["message"].lower()

    def test_dataframe_no_truncation_when_under_limit(self):
        # Create a DataFrame smaller than MAX_DATA_ROWS
        small_df = pd.DataFrame({"col1": range(5), "col2": [f"value_{i}" for i in range(5)]})
        result = serialize_dataframe(small_df)

        assert result["row_count"] == 5
        assert len(result["data"]["rows"]) == 5
        assert "message" not in result

    def test_dataframe_at_exact_limit(self):
        # Create a DataFrame exactly at MAX_DATA_ROWS
        exact_df = pd.DataFrame({"col1": range(MAX_DATA_ROWS), "col2": [f"value_{i}" for i in range(MAX_DATA_ROWS)]})
        result = serialize_dataframe(exact_df)

        assert result["row_count"] == MAX_DATA_ROWS
        assert len(result["data"]["rows"]) == MAX_DATA_ROWS
        assert "message" not in result

    def test_dataframe_with_complex_index(self):
        df = pd.DataFrame({"value": [1, 2, 3]})
        df.index = ["row_a", "row_b", "row_c"]
        result = serialize_dataframe(df)

        rows = result["data"]["rows"]
        # First column should contain the index values
        assert rows[0][0] == "row_a"
        assert rows[1][0] == "row_b"
        assert rows[2][0] == "row_c"

    def test_dataframe_with_special_values(self):
        df = pd.DataFrame(
            {"col1": [float("inf"), float("-inf"), float("nan")], "col2": ["normal", "", "  whitespace  "]}
        )
        result = serialize_dataframe(df)

        rows = result["data"]["rows"]
        # Check that special float values are handled
        assert rows[0][1] == "inf"
        assert rows[1][1] == "-inf"
        assert rows[2][1] is None  # NaN should become None

    def test_serialization_preserves_column_order(self):
        df = pd.DataFrame({"z_column": [1, 2], "a_column": [3, 4], "m_column": [5, 6]})
        result = serialize_dataframe(df)

        # Should preserve original column order, not alphabetical
        expected_columns = ["index", "z_column", "a_column", "m_column"]
        assert result["data"]["columns"] == expected_columns
