"""Unit tests for get_frontmatter function."""

from toolfront.environment import get_frontmatter


def test_parse_markdown_with_tools():
    """Test parsing markdown with tools frontmatter."""
    markdown = """---
tools:
  - python3 script.py
  - bash ls -la
---
# Title

Some content"""

    frontmatter = get_frontmatter(markdown)
    assert "tools" in frontmatter
    assert frontmatter["tools"] == ["python3 script.py", "bash ls -la"]


def test_parse_markdown_without_frontmatter():
    """Test parsing markdown without frontmatter."""
    markdown = "# Title\n\nSome content"
    frontmatter = get_frontmatter(markdown)
    assert frontmatter == {}


def test_parse_markdown_with_invalid_yaml():
    """Test that invalid YAML frontmatter returns empty dict."""
    markdown = """---
[this is: invalid yaml
---
# Title"""

    frontmatter = get_frontmatter(markdown)
    # When YAML parsing fails, it returns empty dict
    assert frontmatter == {}
