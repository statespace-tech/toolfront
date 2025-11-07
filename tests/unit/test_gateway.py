import base64
import hashlib
from pathlib import Path

import httpx
import pytest
from toolfront.lib.gateway import EnvironmentFile, GatewayClient


class TestScanMarkdownFiles:
    def test_scans_single_file(self, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text("# Hello")

        client = GatewayClient("https://example.com", "key")
        files = client.scan_markdown_files(tmp_path)

        assert len(files) == 1
        assert files[0].path == "test.md"

    def test_scans_nested_files(self, tmp_path):
        (tmp_path / "dir").mkdir()
        (tmp_path / "root.md").write_text("root")
        (tmp_path / "dir" / "nested.md").write_text("nested")

        client = GatewayClient("https://example.com", "key")
        files = client.scan_markdown_files(tmp_path)

        assert len(files) == 2
        assert files[0].path == "dir/nested.md"
        assert files[1].path == "root.md"

    def test_ignores_non_markdown(self, tmp_path):
        (tmp_path / "test.md").write_text("markdown")
        (tmp_path / "test.txt").write_text("text")

        client = GatewayClient("https://example.com", "key")
        files = client.scan_markdown_files(tmp_path)

        assert len(files) == 1
        assert files[0].path == "test.md"

    def test_base64_encodes_content(self, tmp_path):
        content = "# Test Content"
        md_file = tmp_path / "test.md"
        md_file.write_text(content)

        client = GatewayClient("https://example.com", "key")
        files = client.scan_markdown_files(tmp_path)

        expected_encoded = base64.b64encode(content.encode()).decode()
        assert files[0].content == expected_encoded

    def test_computes_sha256_checksum(self, tmp_path):
        content = "# Test Content"
        md_file = tmp_path / "test.md"
        md_file.write_text(content)

        client = GatewayClient("https://example.com", "key")
        files = client.scan_markdown_files(tmp_path)

        expected_hash = hashlib.sha256(content.encode()).hexdigest()
        assert files[0].checksum == f"sha256:{expected_hash}"


class TestDeployEnvironment:
    def test_posts_to_correct_endpoint(self, httpx_mock):
        httpx_mock.add_response(json={"data": {"id": "env-123"}})

        client = GatewayClient("https://example.com", "api-key")
        files = [EnvironmentFile(path="test.md", content="encoded", checksum="sha256:abc")]

        client.deploy_environment("test-env", files)

        request = httpx_mock.get_request()
        assert request.url == "https://example.com/api/v1/environments"
        assert request.headers["authorization"] == "Bearer api-key"

    def test_sends_correct_payload(self, httpx_mock):
        httpx_mock.add_response(json={"data": {"id": "env-123"}})

        client = GatewayClient("https://example.com", "api-key")
        files = [EnvironmentFile(path="test.md", content="YWJj", checksum="sha256:abc")]

        client.deploy_environment("my-env", files)

        request = httpx_mock.get_request()
        payload = request.read().decode()
        assert '"name":"my-env"' in payload
        assert '"path":"test.md"' in payload
        assert '"content":"YWJj"' in payload

    def test_returns_deploy_result(self, httpx_mock):
        httpx_mock.add_response(
            json={
                "data": {
                    "id": "env-123",
                    "auth_token": "token-abc",
                    "url": "https://cf.example.com",
                    "fly_url": "https://fly.example.com",
                }
            }
        )

        client = GatewayClient("https://example.com", "api-key")
        result = client.deploy_environment("test", [])

        assert result.id == "env-123"
        assert result.auth_token == "token-abc"
        assert result.url == "https://cf.example.com"
        assert result.fly_url == "https://fly.example.com"

    def test_raises_on_error_response(self, httpx_mock):
        httpx_mock.add_response(status_code=400, text="Bad request")

        client = GatewayClient("https://example.com", "api-key")

        with pytest.raises(RuntimeError, match="Environment creation failed: 400"):
            client.deploy_environment("test", [])
