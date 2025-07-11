"""Unit tests for pattern matching algorithms - standalone functions."""

from toolfront.utils import SearchMode, search_items


class TestRegexPatternMatching:
    """Test regex-based table pattern matching."""

    def test_exact_match(self, sample_table_names):
        result = search_items(sample_table_names, "users", SearchMode.REGEX, 10)
        assert "users" in result
        assert len(result) <= 10

    def test_partial_match(self, sample_table_names):
        result = search_items(sample_table_names, "user", SearchMode.REGEX, 10)
        expected = ["users", "user_profiles"]
        assert all(name in result for name in expected)

    def test_case_sensitive_match(self, sample_table_names):
        result = search_items(sample_table_names, "USER", SearchMode.REGEX, 10)
        assert not len(result)

    def test_wildcard_pattern(self, sample_table_names):
        result = search_items(sample_table_names, ".*_data", SearchMode.REGEX, 10)
        expected = ["customer_data", "payroll_data"]
        assert all(name in result for name in expected)

    def test_no_matches(self, sample_table_names):
        result = search_items(sample_table_names, "nonexistent", SearchMode.REGEX, 10)
        assert result == []

    def test_limit_respected(self, sample_table_names):
        # Pattern that matches many tables
        result = search_items(sample_table_names, ".*", SearchMode.REGEX, 3)
        assert len(result) == 3

    def test_empty_table_list(self):
        result = search_items([], "users", SearchMode.REGEX, 10)
        assert result == []


class TestJaroWinklerPatternMatching:
    """Test Jaro-Winkler similarity-based table pattern matching."""

    def test_exact_match_highest_score(self, sample_table_names):
        result = search_items(sample_table_names, "users", SearchMode.JARO_WINKLER, 10)
        # Exact match should be first (highest similarity)
        assert result[0] == "users"

    def test_similar_names_ranked(self, sample_table_names):
        result = search_items(sample_table_names, "user", SearchMode.JARO_WINKLER, 10)
        # "users" should rank higher than "user_profiles" for pattern "user"
        assert result.index("users") < result.index("user_profiles")

    def test_limit_respected(self, sample_table_names):
        result = search_items(sample_table_names, "data", SearchMode.JARO_WINKLER, 3)
        assert len(result) == 3

    def test_empty_table_list(self):
        result = search_items([], "users", SearchMode.JARO_WINKLER, 10)
        assert result == []


class TestBM25PatternMatching:
    """Test BM25 similarity-based table pattern matching."""

    def test_exact_token_match(self, sample_table_names):
        result = search_items(sample_table_names, "users", SearchMode.BM25, 5)
        # "users" should rank highly for exact token match
        assert "users" in result[:2]

    def test_empty_query_returns_empty(self, sample_table_names):
        result = search_items(sample_table_names, "", SearchMode.BM25, 5)
        assert result == []

    def test_empty_query_whitespace_only(self, sample_table_names):
        # Whitespace gets tokenized as no tokens
        result = search_items(sample_table_names, "   ", SearchMode.BM25, 5)
        assert len(result) == 0  # Should return results based on BM25 scoring

    def test_no_valid_tokens_in_tables(self):
        # Tables with only separators that produce no tokens
        tables = ["___", "...", "---"]
        result = search_items(tables, "users", SearchMode.BM25, 3)
        assert result == []

    def test_limit_respected(self, sample_table_names):
        # Test that limit is respected when there are many matches
        result = search_items(sample_table_names, "data", SearchMode.BM25, 1)
        assert len(result) <= 1
        if result:
            # If we got a result, it should be one of the tables containing "data"
            assert "data" in result[0]

    def test_empty_table_list(self):
        result = search_items([], "users", SearchMode.BM25, 10)
        assert result == []

    def test_relevance_ranking(self, sample_table_names):
        # Test that BM25 ranks more relevant results higher
        result = search_items(sample_table_names, "user", SearchMode.BM25, 5)
        if len(result) >= 2:
            # "users" and "user_profiles" should rank high for query "user"
            top_results = result[:2]
            assert any("user" in name.lower() for name in top_results)
