"""
Demonstrates the DataFrame type hint workflow:
1. Natural language query → LLM generates SQL
2. DataFrame type hint → returns raw data (no truncation)
3. Export to CSV with zero token consumption
"""

import os
import sqlite3
import tempfile
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from toolfront import Database

load_dotenv()


def setup_sqlite_database(db_path: str, num_rows: int = 50000):
    """Create and populate a SQLite database with test data."""
    print(f"Setting up database with {num_rows:,} rows...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE sales_transactions (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            transaction_date DATE,
            product_name TEXT,
            category TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_amount REAL,
            payment_method TEXT,
            status TEXT,
            region TEXT,
            notes TEXT
        )
    """)

    batch_size = 1000
    for batch_start in range(0, num_rows, batch_size):
        batch_data = []
        for i in range(batch_start, min(batch_start + batch_size, num_rows)):
            customer_id = 1000 + (i % 5000)
            days_ago = i % 365
            product_id = i % 100
            category = ["Electronics", "Clothing", "Food", "Home", "Sports"][i % 5]
            quantity = 1 + (i % 10)
            unit_price = round(10 + (i % 990) + 0.99, 2)
            total_amount = round(quantity * unit_price, 2)
            payment = ["Credit Card", "PayPal", "Cash", "Debit Card"][i % 4]
            status = ["Completed", "Pending", "Shipped"][i % 3]
            region = ["North America", "Europe", "Asia", "South America"][i % 4]

            batch_data.append(
                (
                    i + 1,
                    customer_id,
                    f"2024-{1 + (days_ago // 30):02d}-{1 + (days_ago % 28):02d}",
                    f"Product_{product_id:03d}",
                    category,
                    quantity,
                    unit_price,
                    total_amount,
                    payment,
                    status,
                    region,
                    f"Order {i + 1} note",
                )
            )

        cursor.executemany("INSERT INTO sales_transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", batch_data)

    conn.commit()
    conn.close()
    print(f"✅ Database ready with {num_rows:,} rows")


def demo():
    """Demonstrate DataFrame type hint workflow."""

    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ API key required (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        return

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        setup_sqlite_database(db_path, num_rows=100000)

        db = Database(url=f"sqlite:///{db_path}")
        print(f"Connected to database with {len(db.tables)} tables")

        model = "openai:gpt-4o"

        print("\n1. Natural language query with DataFrame type hint:")
        start_time = time.time()
        data: pd.DataFrame | None = db.ask("Show me all sales_transactions data for analysis", model=model)

        if data is None:
            print("❌ Query failed")
            return

        print(f"✅ Retrieved {data.shape[0]:,} rows in {time.time() - start_time:.1f}s")
        print(f"   Columns: {len(data.columns)}, Memory: {data.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")

        print("\n2. Export to CSV:")
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        csv_file = output_dir / "large_export.csv"

        data.to_csv(csv_file, index=False)
        file_size = csv_file.stat().st_size
        print(f"✅ Exported {len(data):,} rows to CSV ({file_size / 1024 / 1024:.1f} MB)")

    finally:
        db_path = Path(db_path)
        if db_path.exists():
            db_path.unlink()


if __name__ == "__main__":
    print("=" * 50)
    demo()
