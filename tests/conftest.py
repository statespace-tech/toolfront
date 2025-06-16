"""Shared test configuration and fixtures."""

import os

import pandas as pd
import pytest
from sqlalchemy.engine.url import make_url

# Note: pytest-asyncio needed for async tests


@pytest.fixture
def sample_table_names():
    """Sample table names for pattern matching tests."""
    return [
        "users",
        "user_profiles",
        "customer_data",
        "orders",
        "order_items",
        "products",
        "product_categories",
        "sales_metrics",
        "financial_reports",
        "inventory_tracking",
        "employee_records",
        "payroll_data",
        "marketing_campaigns",
        "analytics_events",
        "system_logs",
    ]


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for serialization tests."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, None],
            "name": ["Alice", "Bob", "Charlie", ""],
            "value": [10.5, 20.0, None, 0.0],
            "active": [True, False, True, None],
        }
    )


@pytest.fixture
def mock_url():
    """Create a mock URL for testing."""
    return make_url("sqlite:///:memory:")


@pytest.fixture
def postgres_url():
    """PostgreSQL connection URL for integration tests."""
    return os.getenv("POSTGRES_URL", "postgresql://testuser:testpass@localhost:5432/testdb")


@pytest.fixture
def mysql_url():
    """MySQL connection URL for integration tests."""
    return os.getenv("MYSQL_URL", "mysql://testuser:testpass@localhost:3306/testdb")


@pytest.fixture
def sqlserver_url():
    """SQL Server connection URL for integration tests."""
    return os.getenv("SQLSERVER_URL", "mssql://sa:TestPass123!@localhost:1433/master")


@pytest.fixture
def sqlite_url():
    """SQLite connection URL for integration tests."""
    return "sqlite:///:memory:"


@pytest.fixture
def duckdb_url():
    """DuckDB connection URL for integration tests."""
    return "duckdb:///:memory:"
