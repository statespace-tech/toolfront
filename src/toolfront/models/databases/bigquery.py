import asyncio
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

from toolfront.cache import cache
from toolfront.config import CACHE_TTL
from toolfront.models.database import ConnectionResult, Database, DatabaseError

# BigQuery-specific concurrency limits
# BigQuery API can handle ~100 concurrent requests per project, but we want to be conservative
# Also consider memory usage - each operation can hold significant data
MAX_CONCURRENT_DATASETS = min(
    20,  # Conservative limit for BigQuery API
    # Scale with CPU but have a minimum
    max(4, multiprocessing.cpu_count() // 2),
)


class BigQuery(Database):
    @property
    def credentials(self) -> Any:
        credentials_path = self.url.query.get("credentials_path", None)
        if not credentials_path:
            raise ValueError("credentials_path is required in URL parameters")

        return service_account.Credentials.from_service_account_file(credentials_path)

    @property
    def project(self) -> str:
        return self.url.host or ""

    @property
    def client(self) -> bigquery.Client:
        return bigquery.Client(credentials=self.credentials)

    async def test_connection(self) -> ConnectionResult:
        """Test the connection to the database."""

        try:
            await self.query(code="SELECT 1")
            return ConnectionResult(connected=True, message="Connection successful")
        except Exception as e:
            return ConnectionResult(connected=False, message=f"Connection failed: {e}")

    async def query(self, code: str) -> pd.DataFrame:
        """Execute a SQL query and return results as a DataFrame."""
        query_job = self.client.query(code)
        return query_job.to_dataframe()

    @cache(expire=CACHE_TTL)
    async def get_tables(self) -> list[str]:
        """
        List all tables from BigQuery datasets in parallel with controlled concurrency.

        NOTE: We use Google's BigQuery API instead of SQLAlchemy because it's more efficient and avoids permission issues.
        """

        # We need to pass the project to the client if it's not the default project
        client = bigquery.Client(project=self.project, credentials=self.credentials)

        # Get all datasets
        datasets = list(client.list_datasets())

        # Control concurrency to avoid exceeding thread limits
        # Limit concurrent operations
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_DATASETS)

        # Use a single ThreadPoolExecutor with limited workers
        executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DATASETS)

        async def get_dataset_tables(dataset: Any) -> list[str]:
            """Get all table names for a single dataset with semaphore control."""
            async with semaphore:  # Limit concurrent access
                loop = asyncio.get_event_loop()

                try:
                    tables = await loop.run_in_executor(executor, lambda: list(client.list_tables(dataset.dataset_id)))
                    return [f"{self.project}.{dataset.dataset_id}.{table.table_id}" for table in tables]
                except Exception as e:
                    raise DatabaseError(f"Error processing dataset {dataset.dataset_id}: {e}")

        try:
            # Process all datasets with controlled concurrency
            results = await asyncio.gather(
                *[get_dataset_tables(dataset) for dataset in datasets], return_exceptions=True
            )

            # Collect all table names, handling any exceptions
            all_tables: list[str] = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    raise DatabaseError(f"Error processing dataset {datasets[i].dataset_id}: {result}")
                elif isinstance(result, list):
                    all_tables.extend(result)
                else:
                    # Unexpected result type, skip it
                    continue

            return all_tables

        finally:
            # Clean up the executor
            executor.shutdown(wait=False)

    async def inspect_table(self, table_path: str) -> Any:
        """Inspect a specific table's schema."""

        schema = self.client.get_table(table_path).schema

        df = pd.DataFrame(
            [
                {
                    "column_name": field.name,
                    "data_type": field.field_type,
                    "mode": field.mode,
                    "description": field.description,
                }
                for field in schema
            ]
        )
        return df

    async def sample_table(self, table_path: str, n: int = 5) -> Any:
        """Sample n random rows from a table.

        Uses RAND() for random sampling.
        """

        code = f"""
            SELECT *
            FROM {table_path}
            ORDER BY RAND()
            LIMIT {n}
        """
        return await self.query(code=code)
