# """Unit tests for utility functions."""


from toolfront.utils import tokenize


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
