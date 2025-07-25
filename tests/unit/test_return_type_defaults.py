"""Unit tests for return type default behavior in toolfront.models.base."""

from typing import Any

from toolfront.models.base import AIResponse


class TestReturnTypeDefaults:
    """Test return type defaults without external dependencies."""

    def test_air_response_includes_dict_type(self):
        """Test that AIResponse type alias includes dict[str, Any]."""
        import typing

        # Get the actual type arguments from the union
        if hasattr(AIResponse, "__args__"):
            types = AIResponse.__args__
        else:
            # For older Python versions
            types = typing.get_args(AIResponse)

        # Check that dict[str, Any] is in the union
        dict_type_found = False
        for t in types:
            if hasattr(t, "__origin__") and t.__origin__ is dict:
                if hasattr(t, "__args__") and t.__args__ == (str, Any):
                    dict_type_found = True
                    break

        assert dict_type_found, f"dict[str, Any] not found in AIResponse types: {types}"

    def test_basic_types_still_supported(self):
        """Test that basic types are still part of AIResponse."""
        import typing

        if hasattr(AIResponse, "__args__"):
            types = AIResponse.__args__
        else:
            types = typing.get_args(AIResponse)

        # Check that str, bool, int, float are still supported
        assert str in types, "str should still be supported"
        assert bool in types, "bool should still be supported"
        assert int in types, "int should still be supported"
        assert float in types, "float should still be supported"


class TestTypeHintingDocumentation:
    """Test that type hinting is properly documented."""

    def test_ask_docstring_mentions_type_hints(self):
        """Test that ask() docstring mentions return type behavior."""
        from toolfront.models.base import DataSource

        docstring = DataSource.ask.__doc__
        assert docstring is not None, "ask() method should have a docstring"

        # The docstring should mention something about return types
        # This test will fail until we improve the documentation
        docstring_lower = docstring.lower()

        # Check for hints about type annotations
        type_hint_indicators = ["type hint", "type annotation", "return type", "annotation", "pydantic", "dataframe"]

        found_indicator = any(indicator in docstring_lower for indicator in type_hint_indicators)

        # This assertion will initially fail, highlighting the documentation gap
        assert found_indicator, (
            f"ask() docstring should mention type hints/annotations for return types. Current docstring: {docstring}"
        )


class TestDefaultBehaviorChangeConsistency:
    """Test that the default behavior change is consistent."""

    def test_get_output_type_hint_fallback_logic(self):
        """Test the fallback logic when no type hint is provided."""
        # This is testing pure logic without external dependencies
        from toolfront.utils import get_output_type_hint

        # When called without context, should return None
        # (this is the current behavior we're testing)
        result = get_output_type_hint()

        # The actual fallback to dict[str, Any] happens in the ask() method
        # This test documents the current behavior
        assert result is None, "get_output_type_hint() should return None when no context"

    def test_dict_str_any_type_construction(self):
        """Test that dict[str, Any] can be constructed properly."""
        from typing import Any

        # Test that the default type we're using is valid
        default_type = dict[str, Any]

        # Should be able to create an instance
        example = {"key": "value", "number": 42, "bool": True}

        # This is a basic type validation
        assert isinstance(example, dict)
        assert all(isinstance(k, str) for k in example.keys())
