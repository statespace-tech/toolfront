"""Unit tests for ToolFront CLI commands."""

from click.testing import CliRunner

from toolfront.main import cli


def test_cli_help():
    """Test that the main CLI help works."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "browser" in result.output
    assert "database" in result.output
    assert "document" in result.output
