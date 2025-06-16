"""Shared configuration and fixtures for integration tests."""

import asyncio
import time

import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Test database configurations
DATABASE_CONFIGS = {
    "postgresql": {
        "url": "postgresql://testuser:testpass@localhost:5432/testdb",
        "driver": "postgresql+psycopg2",
        "container_name": "test-postgres",
        "health_check_query": "SELECT 1",
    },
    "mysql": {
        "url": "mysql://testuser:testpass@localhost:3306/testdb",
        "driver": "mysql+pymysql",
        "container_name": "test-mysql",
        "health_check_query": "SELECT 1",
    },
    "sqlserver": {
        "url": "mssql://sa:TestPass123!@localhost:1433/master",
        "driver": "mssql+pyodbc",
        "container_name": "test-sqlserver",
        "health_check_query": "SELECT 1",
    },
    "sqlite": {
        "url": "sqlite:///:memory:",
        "driver": "sqlite",
        "health_check_query": "SELECT 1",
    },
    "duckdb": {
        "url": "duckdb:///:memory:",
        "driver": "duckdb",
        "health_check_query": "SELECT 1",
    },
}


def wait_for_database(url: str, max_retries: int = 30, delay: float = 1.0) -> bool:
    """Wait for database to be ready with exponential backoff."""
    for attempt in range(max_retries):
        try:
            engine = create_engine(url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            engine.dispose()
            return True
        except OperationalError:
            if attempt < max_retries - 1:
                wait_time = min(delay * (2**attempt), 10.0)  # Cap at 10 seconds
                time.sleep(wait_time)
            continue
        except Exception as e:
            print(f"Unexpected error connecting to {url}: {e}")
            return False
    return False


@pytest.fixture
def postgres_url() -> str | None:
    """Fixture providing PostgreSQL connection URL if available."""
    url = DATABASE_CONFIGS["postgresql"]["url"]
    if wait_for_database(url):
        return url
    pytest.skip("PostgreSQL not available")


@pytest.fixture
def mysql_url() -> str | None:
    """Fixture providing MySQL connection URL if available."""
    url = DATABASE_CONFIGS["mysql"]["url"]
    if wait_for_database(url):
        return url
    pytest.skip("MySQL not available")


@pytest.fixture
def sqlserver_url() -> str | None:
    """Fixture providing SQL Server connection URL if available."""
    url = DATABASE_CONFIGS["sqlserver"]["url"]
    if wait_for_database(url):
        return url
    pytest.skip("SQL Server not available")


@pytest.fixture
def sqlite_url() -> str:
    """Fixture providing SQLite in-memory connection URL."""
    return DATABASE_CONFIGS["sqlite"]["url"]


@pytest.fixture
def duckdb_url() -> str:
    """Fixture providing DuckDB in-memory connection URL."""
    return DATABASE_CONFIGS["duckdb"]["url"]


@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Sample test data for integration tests."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "email": [
                "alice@example.com",
                "bob@example.com",
                "charlie@example.com",
                "diana@example.com",
                "eve@example.com",
            ],
            "age": [25, 30, 35, 28, 32],
            "active": [True, True, False, True, True],
        }
    )


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
