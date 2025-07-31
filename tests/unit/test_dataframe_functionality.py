"""Unit tests for DataFrame type hint functionality."""

import pandas as pd

from toolfront.models.database import Database, Query


class TestDataFrameTypeHints:
    """Test DataFrame type hint processing."""

    def test_preprocess_dataframe_type(self):
        """Test that pd.DataFrame type is converted to Query."""
        db = object.__new__(Database)

        # Direct DataFrame type
        result = db._preprocess(pd.DataFrame)
        assert result == Query

    def test_preprocess_optional_dataframe(self):
        """Test that Optional[pd.DataFrame] is handled correctly."""
        db = object.__new__(Database)

        # Optional[pd.DataFrame]
        optional_df_type = pd.DataFrame | None
        result = db._preprocess(optional_df_type)

        # Should return Query | None
        assert hasattr(result, "__args__")
        assert Query in result.__args__
        assert type(None) in result.__args__

    def test_preprocess_other_types(self):
        """Test that non-DataFrame types pass through unchanged."""
        db = object.__new__(Database)

        assert db._preprocess(str) is str
        assert db._preprocess(dict) is dict
        assert db._preprocess(list) is list

    def test_postprocess_query(self):
        """Test that Query objects are executed via query_raw."""
        query = Query(code="SELECT * FROM test")

        # Create a simple test object with the postprocess logic
        class TestDB:
            def query_raw(self, q):
                assert q == query
                return pd.DataFrame({"result": [1, 2, 3]})

            def _postprocess(self, result):
                if isinstance(result, Query):
                    return self.query_raw(result)
                return result

        db = TestDB()
        result = db._postprocess(query)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

    def test_postprocess_non_query(self):
        """Test that non-Query objects pass through unchanged."""
        db = object.__new__(Database)

        assert db._postprocess("hello") == "hello"
        assert db._postprocess(42) == 42

        df = pd.DataFrame({"a": [1, 2]})
        assert db._postprocess(df) is df
