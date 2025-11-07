from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner
from toolfront.cli.deploy import deploy
from toolfront.lib.gateway import DeployResult, EnvironmentFile


@pytest.fixture
def runner():
    return CliRunner()


class TestDeployCommand:
    def test_requires_api_key(self, runner, tmp_path):
        result = runner.invoke(deploy, [str(tmp_path)])
        assert result.exit_code != 0
        assert "api-key" in result.output.lower() or "TOOLFRONT_API_KEY" in result.output

    def test_uses_directory_name_as_default_env_name(self, runner, tmp_path):
        (tmp_path / "test.md").write_text("content")

        with patch("toolfront.cli.deploy.GatewayClient") as mock_client:
            mock_instance = Mock()
            mock_instance.scan_markdown_files.return_value = [
                EnvironmentFile(path="test.md", content="abc", checksum="sha256:123")
            ]
            mock_instance.deploy_environment.return_value = DeployResult(
                id="env-123", auth_token=None, url=None, fly_url=None
            )
            mock_client.return_value = mock_instance

            result = runner.invoke(deploy, [str(tmp_path), "--api-key", "test-key"])

            mock_instance.deploy_environment.assert_called_once()
            call_args = mock_instance.deploy_environment.call_args
            assert call_args[0][0] == tmp_path.name

    def test_uses_custom_name_when_provided(self, runner, tmp_path):
        (tmp_path / "test.md").write_text("content")

        with patch("toolfront.cli.deploy.GatewayClient") as mock_client:
            mock_instance = Mock()
            mock_instance.scan_markdown_files.return_value = [
                EnvironmentFile(path="test.md", content="abc", checksum="sha256:123")
            ]
            mock_instance.deploy_environment.return_value = DeployResult(
                id="env-123", auth_token=None, url=None, fly_url=None
            )
            mock_client.return_value = mock_instance

            result = runner.invoke(deploy, [str(tmp_path), "--api-key", "test-key", "--name", "custom-name"])

            mock_instance.deploy_environment.assert_called_once()
            call_args = mock_instance.deploy_environment.call_args
            assert call_args[0][0] == "custom-name"

    def test_displays_deployment_results(self, runner, tmp_path):
        (tmp_path / "test.md").write_text("content")

        with patch("toolfront.cli.deploy.GatewayClient") as mock_client:
            mock_instance = Mock()
            mock_instance.scan_markdown_files.return_value = [
                EnvironmentFile(path="test.md", content="abc", checksum="sha256:123")
            ]
            mock_instance.deploy_environment.return_value = DeployResult(
                id="env-123",
                auth_token="token-abc",
                url="https://cf.example.com",
                fly_url="https://fly.example.com",
            )
            mock_client.return_value = mock_instance

            result = runner.invoke(deploy, [str(tmp_path), "--api-key", "test-key"])

            assert result.exit_code == 0
            assert "env-123" in result.output
            assert "https://cf.example.com" in result.output
            assert "https://fly.example.com" in result.output
            assert "token-abc" in result.output

    def test_warns_when_no_markdown_files(self, runner, tmp_path):
        with patch("toolfront.cli.deploy.GatewayClient") as mock_client:
            mock_instance = Mock()
            mock_instance.scan_markdown_files.return_value = []
            mock_client.return_value = mock_instance

            result = runner.invoke(deploy, [str(tmp_path), "--api-key", "test-key"])

            assert "No markdown files found" in result.output
            mock_instance.deploy_environment.assert_not_called()

    def test_handles_deployment_errors(self, runner, tmp_path):
        (tmp_path / "test.md").write_text("content")

        with patch("toolfront.cli.deploy.GatewayClient") as mock_client:
            mock_instance = Mock()
            mock_instance.scan_markdown_files.return_value = [
                EnvironmentFile(path="test.md", content="abc", checksum="sha256:123")
            ]
            mock_instance.deploy_environment.side_effect = RuntimeError("API error")
            mock_client.return_value = mock_instance

            result = runner.invoke(deploy, [str(tmp_path), "--api-key", "test-key"])

            assert result.exit_code != 0
            assert "API error" in result.output
