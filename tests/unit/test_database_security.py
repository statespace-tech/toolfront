"""Unit tests for database security functions."""

from toolfront.commands.database import is_read_only_query


class TestIsReadOnlyQuery:
    """Test SQL query validation for read-only enforcement."""

    def test_select_queries_allowed(self):
        """Test that SELECT queries are allowed."""
        queries = [
            "SELECT * FROM users",
            "SELECT id, name FROM products WHERE price > 100",
            "SELECT COUNT(*) FROM orders",
            "select * from users",  # lowercase
            "  SELECT * FROM users  ",  # whitespace
        ]
        for sql in queries:
            assert is_read_only_query(sql) is True

    def test_with_cte_queries_allowed(self):
        """Test that WITH (CTE) queries are allowed."""
        queries = [
            "WITH cte AS (SELECT * FROM users) SELECT * FROM cte",
            """WITH RECURSIVE cte AS (
                SELECT 1 as n
                UNION ALL
                SELECT n + 1 FROM cte WHERE n < 10
            ) SELECT * FROM cte""",
        ]
        for sql in queries:
            assert is_read_only_query(sql) is True

    def test_insert_queries_blocked(self):
        """Test that INSERT queries are blocked."""
        queries = [
            "INSERT INTO users (name) VALUES ('John')",
            "INSERT INTO products SELECT * FROM temp_products",
            "insert into users values (1, 'test')",  # lowercase
        ]
        for sql in queries:
            assert is_read_only_query(sql) is False

    def test_update_queries_blocked(self):
        """Test that UPDATE queries are blocked."""
        queries = [
            "UPDATE users SET name = 'John' WHERE id = 1",
            "UPDATE products SET price = price * 1.1",
            "update users set active = false",  # lowercase
        ]
        for sql in queries:
            assert is_read_only_query(sql) is False

    def test_delete_queries_blocked(self):
        """Test that DELETE queries are blocked."""
        queries = [
            "DELETE FROM users WHERE id = 1",
            "DELETE FROM products",
            "delete from orders where status = 'cancelled'",  # lowercase
        ]
        for sql in queries:
            assert is_read_only_query(sql) is False

    def test_drop_queries_blocked(self):
        """Test that DROP queries are blocked."""
        queries = [
            "DROP TABLE users",
            "DROP DATABASE test_db",
            "DROP INDEX idx_users_name",
            "drop view user_view",  # lowercase
        ]
        for sql in queries:
            assert is_read_only_query(sql) is False

    def test_create_queries_blocked(self):
        """Test that CREATE queries are blocked."""
        queries = [
            "CREATE TABLE users (id INT, name VARCHAR(100))",
            "CREATE DATABASE test_db",
            "CREATE INDEX idx_users_name ON users(name)",
            "create view user_view as select * from users",  # lowercase
        ]
        for sql in queries:
            assert is_read_only_query(sql) is False

    def test_alter_queries_blocked(self):
        """Test that ALTER queries are blocked."""
        queries = [
            "ALTER TABLE users ADD COLUMN email VARCHAR(255)",
            "ALTER TABLE products DROP COLUMN description",
            "alter database test_db set timezone = 'UTC'",  # lowercase
        ]
        for sql in queries:
            assert is_read_only_query(sql) is False

    def test_truncate_queries_blocked(self):
        """Test that TRUNCATE queries are blocked."""
        queries = [
            "TRUNCATE TABLE users",
            "TRUNCATE products",
            "truncate table orders",  # lowercase
        ]
        for sql in queries:
            assert is_read_only_query(sql) is False

    def test_exec_queries_blocked(self):
        """Test that EXEC/EXECUTE queries are blocked."""
        queries = [
            "EXEC sp_help",
            "EXECUTE stored_procedure",
            "CALL my_function()",
        ]
        for sql in queries:
            assert is_read_only_query(sql) is False

    def test_grant_revoke_blocked(self):
        """Test that GRANT/REVOKE queries are blocked."""
        queries = [
            "GRANT SELECT ON users TO john",
            "REVOKE ALL ON products FROM public",
        ]
        for sql in queries:
            assert is_read_only_query(sql) is False

    def test_multiple_statements(self):
        """Test handling of multiple SQL statements."""
        # Multiple SELECT statements should be allowed
        sql = "SELECT * FROM users; SELECT * FROM products"
        assert is_read_only_query(sql) is True

        # Mix of read and write should be blocked
        sql = "SELECT * FROM users; DELETE FROM products"
        assert is_read_only_query(sql) is False

    def test_sql_injection_patterns(self):
        """Test that potential SQL injection patterns are handled correctly."""
        # These should still be validated based on the main statement type
        queries = [
            ("SELECT * FROM users WHERE name = 'test'; DROP TABLE users; --'", False),  # Has DROP
            ("SELECT * FROM users WHERE id = 1 OR 1=1", True),  # Still just SELECT
            ("SELECT * FROM users -- DELETE FROM users", False),  # Conservative: blocks even in comments
        ]
        for sql, expected in queries:
            assert is_read_only_query(sql) is expected

    def test_word_boundaries(self):
        """Test that operation keywords are blocked even in strings (conservative approach)."""
        # The function is conservative and blocks keywords even in string literals
        queries = [
            ("SELECT * FROM users WHERE name = 'INSERTED_BY'", True),  # No "INSERT" as whole word
            ("SELECT * FROM deleted_items", True),  # "deleted" != "DELETE"
            ("SELECT * FROM products WHERE description LIKE '%UPDATE%'", False),  # "UPDATE" is a whole word
        ]
        for sql, expected in queries:
            assert is_read_only_query(sql) is expected

    def test_empty_queries(self):
        """Test handling of empty or whitespace queries."""
        queries = ["", "   ", "\n\n", "\t"]
        for sql in queries:
            # Empty queries are considered safe (no write operations)
            assert is_read_only_query(sql) is True
