"""Unit tests for ToolFront CLI commands."""

from click.testing import CliRunner

from toolfront.main import main


def test_cli_help():
    """Test that the main CLI help works."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "mcp" in result.output
    assert "database" in result.output
