import base64
import hashlib
from dataclasses import dataclass
from pathlib import Path

import httpx


@dataclass
class EnvironmentFile:
    path: str
    content: str
    checksum: str


@dataclass
class DeployResult:
    id: str
    auth_token: str | None
    url: str | None
    fly_url: str | None


@dataclass
class Environment:
    id: str
    name: str
    status: str
    url: str | None
    fly_url: str | None
    created_at: str


class GatewayClient:
    def __init__(self, base_url: str, api_key: str, org_id: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.org_id = org_id

    def scan_markdown_files(self, dir_path: Path) -> list[EnvironmentFile]:
        files = []
        for md_file in dir_path.rglob("*.md"):
            if not md_file.is_file():
                continue

            raw_content = md_file.read_bytes()
            encoded = base64.b64encode(raw_content).decode("utf-8")
            checksum_hash = hashlib.sha256(raw_content).hexdigest()
            checksum = f"sha256:{checksum_hash}"
            rel_path = md_file.relative_to(dir_path).as_posix()

            files.append(EnvironmentFile(path=rel_path, content=encoded, checksum=checksum))

        return sorted(files, key=lambda f: f.path)

    def deploy_environment(self, name: str, files: list[EnvironmentFile]) -> DeployResult:
        payload = {
            "name": name,
            "files": [{"path": f.path, "content": f.content, "checksum": f.checksum} for f in files],
        }

        response = httpx.post(
            f"{self.base_url}/api/v1/environments",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=30.0,
        )

        if not response.is_success:
            raise RuntimeError(f"Environment creation failed: {response.status_code}\n{response.text}")

        data = response.json().get("data", response.json())

        return DeployResult(
            id=data["id"],
            auth_token=data.get("auth_token"),
            url=data.get("url"),
            fly_url=data.get("fly_url"),
        )

    def verify_environment(self, url: str, auth_token: str, max_attempts: int = 20, progress_callback=None) -> bool:
        import time

        for attempt in range(1, max_attempts + 1):
            try:
                response = httpx.get(
                    url,
                    headers={"Authorization": f"Bearer {auth_token}"},
                    timeout=10.0,
                    follow_redirects=True,
                )
                if response.is_success:
                    return True
            except (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError) as e:
                if progress_callback:
                    progress_callback(attempt, max_attempts, str(e))
            except httpx.HTTPStatusError:
                pass

            if attempt < max_attempts:
                wait_time = min(2 * attempt, 10)
                time.sleep(wait_time)

        return False

    def list_environments(self) -> list[Environment]:
        response = httpx.get(
            f"{self.base_url}/api/v1/environments",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0,
        )

        if not response.is_success:
            raise RuntimeError(f"Failed to list environments: {response.status_code}\n{response.text}")

        json_response = response.json()
        data = json_response.get("data", json_response) if isinstance(json_response, dict) else json_response

        if not isinstance(data, list):
            data = [data]

        return [
            Environment(
                id=env["id"],
                name=env["name"],
                status=env["status"],
                url=env.get("url"),
                fly_url=env.get("fly_url"),
                created_at=env["created_at"],
            )
            for env in data
        ]

    def delete_environment(self, environment_id: str) -> None:
        response = httpx.delete(
            f"{self.base_url}/api/v1/environments/{environment_id}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0,
        )

        if not response.is_success:
            raise RuntimeError(f"Failed to delete environment: {response.status_code}\n{response.text}")

    def update_environment(self, environment_id: str, files: list[EnvironmentFile]) -> None:
        payload = {
            "files": [{"path": f.path, "content": f.content, "checksum": f.checksum} for f in files],
        }

        response = httpx.post(
            f"{self.base_url}/api/v1/environments/{environment_id}/publish",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=30.0,
        )

        if not response.is_success:
            raise RuntimeError(f"Failed to update environment: {response.status_code}\n{response.text}")

    def create_token(
        self,
        name: str,
        scope: str,
        environment_ids: list[str] | None = None,
        expires_at: str | None = None,
    ) -> dict:
        if not self.org_id:
            raise RuntimeError(
                "Organization ID required for token creation. Set org_id in config or use --org-id flag."
            )

        payload = {
            "organization_id": self.org_id,
            "name": name,
            "scope": f"environments:{scope}",
        }

        if environment_ids:
            payload["allowed_environment_ids"] = environment_ids

        if expires_at:
            payload["expires_at"] = expires_at

        response = httpx.post(
            f"{self.base_url}/api/v1/tokens",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=30.0,
        )

        if not response.is_success:
            raise RuntimeError(f"Failed to create token: {response.status_code}\n{response.text}")

        return response.json().get("data", response.json())

    def list_tokens(self, only_active: bool = True, limit: int = 100, offset: int = 0) -> dict:
        if not self.org_id:
            raise RuntimeError(
                "Organization ID required for listing tokens. Set org_id in config or use --org-id flag."
            )

        response = httpx.get(
            f"{self.base_url}/api/v1/tokens",
            headers={"Authorization": f"Bearer {self.api_key}"},
            params={
                "organization_id": self.org_id,
                "only_active": str(only_active).lower(),
                "limit": limit,
                "offset": offset,
            },
            timeout=30.0,
        )

        if not response.is_success:
            raise RuntimeError(f"Failed to list tokens: {response.status_code}\n{response.text}")

        data = response.json()
        return data.get("data", data) if isinstance(data, dict) else data

    def get_token(self, token_id: str) -> dict:
        response = httpx.get(
            f"{self.base_url}/api/v1/tokens/{token_id}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0,
        )

        if not response.is_success:
            raise RuntimeError(f"Failed to get token: {response.status_code}\n{response.text}")

        return response.json().get("data", response.json())

    def rotate_token(
        self,
        token_id: str,
        name: str | None = None,
        scope: str | None = None,
        environment_ids: list[str] | None = None,
        expires_at: str | None = None,
    ) -> dict:
        payload = {}

        if name is not None:
            payload["name"] = name
        if scope is not None:
            payload["scope"] = f"environments:{scope}"
        if environment_ids is not None:
            payload["environment_scope"] = {"type": "restricted", "environment_ids": environment_ids}
        if expires_at is not None:
            payload["expires_at"] = expires_at

        response = httpx.post(
            f"{self.base_url}/api/v1/tokens/{token_id}/rotate",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=30.0,
        )

        if not response.is_success:
            raise RuntimeError(f"Failed to rotate token: {response.status_code}\n{response.text}")

        return response.json().get("data", response.json())

    def revoke_token(self, token_id: str, reason: str | None = None) -> None:
        payload = {}
        if reason:
            payload["reason"] = reason

        response = httpx.request(
            "DELETE",
            f"{self.base_url}/api/v1/tokens/{token_id}",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=30.0,
        )

        if not response.is_success:
            raise RuntimeError(f"Failed to revoke token: {response.status_code}\n{response.text}")
