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
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

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
                    f"{url}/README.md",
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
