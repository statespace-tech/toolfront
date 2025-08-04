"""Unit tests for database query validation logic."""

from toolfront.models.database import Query


class TestQueryValidation:
    """Test SQL query validation logic - pure logic, no mocks."""

    def test_read_only_queries_allowed(self):
        """Test that read-only queries are correctly identified."""
        read_only_queries = [
            "SELECT * FROM users",
            "SELECT id, name FROM products WHERE price > 100",
            "WITH cte AS (SELECT * FROM orders) SELECT * FROM cte",
            "SHOW TABLES",
            "DESCRIBE users",
            "EXPLAIN SELECT * FROM users",
        ]

        for sql in read_only_queries:
            query = Query(code=sql)
            assert query.is_read_only_query() is True

    def test_write_queries_rejected(self):
        """Test that write queries are correctly identified."""
        write_queries = [
            "INSERT INTO users (name) VALUES ('test')",
            "UPDATE users SET name = 'test' WHERE id = 1",
            "DELETE FROM users WHERE id = 1",
            "DROP TABLE users",
            "CREATE TABLE test (id INT)",
            "ALTER TABLE users ADD COLUMN email VARCHAR(255)",
            "TRUNCATE TABLE users",
        ]

        for sql in write_queries:
            query = Query(code=sql)
            assert query.is_read_only_query() is False

    def test_complex_query_validation(self):
        """Test validation of complex queries."""
        # CTE with SELECT is allowed
        query = Query(
            code="""
            WITH monthly_sales AS (
                SELECT DATE_TRUNC('month', date) as month, SUM(amount) as total
                FROM sales
                GROUP BY 1
            )
            SELECT * FROM monthly_sales
        """
        )
        assert query.is_read_only_query() is True

        # Multiple statements where one is not read-only
        query = Query(
            code="SELECT * FROM users; DELETE FROM users WHERE id = 1")
        assert query.is_read_only_query() is False

    def test_case_insensitive_keywords(self):
        """Test that SQL keywords are case-insensitive."""
        queries = [
            ("select * from users", True),
            ("SELECT * FROM users", True),
            ("SeLeCt * FrOm users", True),
            ("insert into users values (1)", False),
            ("INSERT INTO users VALUES (1)", False),
        ]

        for sql, expected in queries:
            query = Query(code=sql)
            assert query.is_read_only_query() is expected
