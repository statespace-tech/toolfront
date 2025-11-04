"""
End-to-end integration test for deployment and AI agent flow.

Requires environment variables:
- TOOLFRONT_TEST_API_KEY: Gateway API key
- TOOLFRONT_TEST_GATEWAY_URL: Gateway URL (optional, defaults to staging)
- OPENAI_API_KEY: OpenAI API key for agent testing
"""

import os

import pytest
from toolfront import Application


@pytest.mark.skipif(
    not os.getenv("TOOLFRONT_TEST_API_KEY") or not os.getenv("OPENAI_API_KEY"),
    reason="Integration test requires TOOLFRONT_TEST_API_KEY and OPENAI_API_KEY",
)
def test_deploy_and_agent_flow(tmp_path):
    """Test full deployment and AI agent execution flow."""
    from toolfront.lib.gateway import GatewayClient

    gateway_url = os.getenv("TOOLFRONT_TEST_GATEWAY_URL", "https://toolfront-gateway-staging.fly.dev")
    api_key = os.getenv("TOOLFRONT_TEST_API_KEY")

    # Create test markdown files
    test_dir = tmp_path / "test-site"
    test_dir.mkdir()
    (test_dir / "index.md").write_text(
        """---
tools:
  - ["ls", "{path}"]
  - ["cat", "{path}"]
---

# Test Site
This is a test environment for e2e verification.
"""
    )
    (test_dir / "docs.md").write_text("# Documentation\nSome docs here.")

    # Deploy
    client = GatewayClient(gateway_url, api_key)
    files = client.scan_markdown_files(test_dir)
    assert len(files) == 2

    result = client.deploy_environment("e2e-test", files)
    assert result.id
    assert result.auth_token
    env_url = result.fly_url or result.url
    assert env_url

    try:
        # Test AI agent
        app = Application(url=f"{env_url}/index.md", param={"Authorization": f"Bearer {result.auth_token}"})
        response = app.ask("List all files", model="openai:gpt-4o-mini")

        assert "docs.md" in response or "index.md" in response
    finally:
        # Cleanup would go here (delete environment)
        # For now, test environments can be cleaned up manually
        pass
