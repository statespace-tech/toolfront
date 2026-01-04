//! Gateway API client.

use crate::config::Credentials;
use crate::error::{GatewayError, Result};
use crate::gateway::types::{DeployResult, Environment, EnvironmentFile, Token, TokenCreateResult};
use base64::{engine::general_purpose::STANDARD as BASE64, Engine};
use reqwest::Client;
use serde::Serialize;
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::path::Path;
use std::time::Duration;

const USER_AGENT: &str = concat!("statespace-cli/", env!("CARGO_PKG_VERSION"));

const VERIFY_MAX_ATTEMPTS: u32 = 20;
const VERIFY_BASE_DELAY_SECS: u64 = 2;
const VERIFY_MAX_DELAY_SECS: u64 = 10;

#[derive(Clone)]
pub(crate) struct GatewayClient {
    base_url: String,
    api_key: String,
    org_id: Option<String>,
    http: Client,
}

impl GatewayClient {
    pub(crate) fn new(credentials: Credentials) -> Result<Self> {
        let http = Client::builder()
            .user_agent(USER_AGENT)
            .timeout(Duration::from_secs(30))
            .build()
            .map_err(|e| GatewayError::ClientBuild(e.to_string()))?;

        Ok(Self {
            base_url: credentials.api_url,
            api_key: credentials.api_key,
            org_id: credentials.org_id,
            http,
        })
    }

    fn auth_header(&self) -> String {
        format!("Bearer {}", self.api_key)
    }

    fn require_org_id(&self) -> Result<&str> {
        self.org_id
            .as_deref()
            .ok_or_else(|| GatewayError::MissingOrgId.into())
    }

    pub(crate) fn scan_markdown_files(&self, dir: &Path) -> Result<Vec<EnvironmentFile>> {
        let mut files = Vec::new();

        for path in walkdir(dir)? {
            if !path.is_file() {
                continue;
            }
            if path.extension().and_then(|s| s.to_str()) != Some("md") {
                continue;
            }

            let raw = std::fs::read(&path)?;
            let content = BASE64.encode(&raw);

            let mut hasher = Sha256::new();
            hasher.update(&raw);
            let checksum = format!("sha256:{:x}", hasher.finalize());

            let rel_path = path
                .strip_prefix(dir)
                .unwrap_or(&path)
                .to_string_lossy()
                .replace('\\', "/");

            files.push(EnvironmentFile {
                path: rel_path,
                content,
                checksum,
            });
        }

        files.sort_by(|a, b| a.path.cmp(&b.path));
        Ok(files)
    }

    pub(crate) async fn deploy_environment(
        &self,
        name: &str,
        files: Vec<EnvironmentFile>,
    ) -> Result<DeployResult> {
        #[derive(Serialize)]
        struct Payload<'a> {
            name: &'a str,
            files: Vec<EnvironmentFile>,
        }

        let url = format!("{}/api/v1/environments", self.base_url);
        let resp = self
            .http
            .post(&url)
            .header("Authorization", self.auth_header())
            .json(&Payload { name, files })
            .send()
            .await?;

        parse_api_response(resp).await
    }

    pub(crate) async fn list_environments(&self) -> Result<Vec<Environment>> {
        let url = format!("{}/api/v1/environments", self.base_url);
        let resp = self
            .http
            .get(&url)
            .header("Authorization", self.auth_header())
            .send()
            .await?;

        parse_api_list_response(resp).await
    }

    pub(crate) async fn update_environment(
        &self,
        environment_id: &str,
        files: Vec<EnvironmentFile>,
    ) -> Result<()> {
        #[derive(Serialize)]
        struct Payload {
            files: Vec<EnvironmentFile>,
        }

        let url = format!(
            "{}/api/v1/environments/{}/publish",
            self.base_url, environment_id
        );
        let resp = self
            .http
            .post(&url)
            .header("Authorization", self.auth_header())
            .json(&Payload { files })
            .send()
            .await?;

        check_api_response(resp).await
    }

    pub(crate) async fn delete_environment(&self, environment_id: &str) -> Result<()> {
        let url = format!("{}/api/v1/environments/{}", self.base_url, environment_id);
        let resp = self
            .http
            .delete(&url)
            .header("Authorization", self.auth_header())
            .send()
            .await?;

        check_api_response(resp).await
    }

    pub(crate) async fn verify_environment(&self, url: &str, auth_token: &str) -> Result<bool> {
        for attempt in 1..=VERIFY_MAX_ATTEMPTS {
            match self
                .http
                .get(url)
                .header("Authorization", format!("Bearer {auth_token}"))
                .send()
                .await
            {
                Ok(resp) if resp.status().is_success() => return Ok(true),
                _ => {}
            }

            if attempt < VERIFY_MAX_ATTEMPTS {
                let wait = std::cmp::min(VERIFY_BASE_DELAY_SECS * u64::from(attempt), VERIFY_MAX_DELAY_SECS);
                tokio::time::sleep(Duration::from_secs(wait)).await;
            }
        }
        Ok(false)
    }

    pub(crate) async fn create_token(
        &self,
        name: &str,
        scope: &str,
        environment_ids: Option<&[String]>,
        expires_at: Option<&str>,
    ) -> Result<TokenCreateResult> {
        let org_id = self.require_org_id()?;

        #[derive(Serialize)]
        struct Payload<'a> {
            organization_id: &'a str,
            name: &'a str,
            scope: String,
            #[serde(skip_serializing_if = "Option::is_none")]
            allowed_environment_ids: Option<&'a [String]>,
            #[serde(skip_serializing_if = "Option::is_none")]
            expires_at: Option<&'a str>,
        }

        let url = format!("{}/api/v1/tokens", self.base_url);
        let resp = self
            .http
            .post(&url)
            .header("Authorization", self.auth_header())
            .json(&Payload {
                organization_id: org_id,
                name,
                scope: format!("environments:{scope}"),
                allowed_environment_ids: environment_ids,
                expires_at,
            })
            .send()
            .await?;

        parse_api_response(resp).await
    }

    pub(crate) async fn list_tokens(
        &self,
        only_active: bool,
        limit: u32,
        offset: u32,
    ) -> Result<Vec<Token>> {
        let org_id = self.require_org_id()?;

        let url = format!("{}/api/v1/tokens", self.base_url);
        let resp = self
            .http
            .get(&url)
            .header("Authorization", self.auth_header())
            .query(&[
                ("organization_id", org_id),
                ("only_active", if only_active { "true" } else { "false" }),
                ("limit", &limit.to_string()),
                ("offset", &offset.to_string()),
            ])
            .send()
            .await?;

        parse_api_list_response(resp).await
    }

    pub(crate) async fn get_token(&self, token_id: &str) -> Result<Token> {
        let url = format!("{}/api/v1/tokens/{}", self.base_url, token_id);
        let resp = self
            .http
            .get(&url)
            .header("Authorization", self.auth_header())
            .send()
            .await?;

        parse_api_response(resp).await
    }

    pub(crate) async fn rotate_token(
        &self,
        token_id: &str,
        name: Option<&str>,
        scope: Option<&str>,
        environment_ids: Option<&[String]>,
        expires_at: Option<&str>,
    ) -> Result<TokenCreateResult> {
        #[derive(Serialize)]
        struct Payload<'a> {
            #[serde(skip_serializing_if = "Option::is_none")]
            name: Option<&'a str>,
            #[serde(skip_serializing_if = "Option::is_none")]
            scope: Option<String>,
            #[serde(skip_serializing_if = "Option::is_none")]
            environment_scope: Option<EnvironmentScope<'a>>,
            #[serde(skip_serializing_if = "Option::is_none")]
            expires_at: Option<&'a str>,
        }

        #[derive(Serialize)]
        struct EnvironmentScope<'a> {
            #[serde(rename = "type")]
            scope_type: &'a str,
            environment_ids: &'a [String],
        }

        let url = format!("{}/api/v1/tokens/{}/rotate", self.base_url, token_id);
        let resp = self
            .http
            .post(&url)
            .header("Authorization", self.auth_header())
            .json(&Payload {
                name,
                scope: scope.map(|s| format!("environments:{s}")),
                environment_scope: environment_ids.map(|ids| EnvironmentScope {
                    scope_type: "restricted",
                    environment_ids: ids,
                }),
                expires_at,
            })
            .send()
            .await?;

        parse_api_response(resp).await
    }

    pub(crate) async fn revoke_token(&self, token_id: &str, reason: Option<&str>) -> Result<()> {
        #[derive(Serialize)]
        struct Payload<'a> {
            #[serde(skip_serializing_if = "Option::is_none")]
            reason: Option<&'a str>,
        }

        let url = format!("{}/api/v1/tokens/{}", self.base_url, token_id);
        let resp = self
            .http
            .delete(&url)
            .header("Authorization", self.auth_header())
            .json(&Payload { reason })
            .send()
            .await?;

        check_api_response(resp).await
    }
}

fn walkdir(dir: &Path) -> Result<Vec<std::path::PathBuf>> {
    let mut results = Vec::new();
    walk_recursive(dir, &mut results)?;
    Ok(results)
}

fn walk_recursive(dir: &Path, results: &mut Vec<std::path::PathBuf>) -> Result<()> {
    if !dir.is_dir() {
        return Ok(());
    }
    for entry in std::fs::read_dir(dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.is_dir() {
            walk_recursive(&path, results)?;
        } else {
            results.push(path);
        }
    }
    Ok(())
}

async fn check_api_response(resp: reqwest::Response) -> Result<()> {
    let status = resp.status();
    if status.is_success() {
        return Ok(());
    }

    let text = resp
        .text()
        .await
        .unwrap_or_else(|e| format!("(failed to read body: {e})"));
    let message = text.chars().take(512).collect();
    Err(GatewayError::Api { status, message }.into())
}

async fn parse_api_response<T: serde::de::DeserializeOwned>(resp: reqwest::Response) -> Result<T> {
    let status = resp.status();
    let text = resp
        .text()
        .await
        .unwrap_or_else(|e| format!("(failed to read body: {e})"));

    if !status.is_success() {
        let message = text.chars().take(512).collect();
        return Err(GatewayError::Api { status, message }.into());
    }

    let value: Value = serde_json::from_str(&text).map_err(|e| GatewayError::Api {
        status,
        message: format!("invalid JSON: {e}"),
    })?;

    let data = value.get("data").unwrap_or(&value);

    serde_json::from_value(data.clone()).map_err(|e| {
        GatewayError::Api {
            status,
            message: format!("failed to parse response: {e}"),
        }
        .into()
    })
}

async fn parse_api_list_response<T: serde::de::DeserializeOwned>(
    resp: reqwest::Response,
) -> Result<Vec<T>> {
    let status = resp.status();
    let text = resp
        .text()
        .await
        .unwrap_or_else(|e| format!("(failed to read body: {e})"));

    if !status.is_success() {
        let message = text.chars().take(512).collect();
        return Err(GatewayError::Api { status, message }.into());
    }

    let value: Value = serde_json::from_str(&text).map_err(|e| GatewayError::Api {
        status,
        message: format!("invalid JSON: {e}"),
    })?;

    let data = value.get("data").unwrap_or(&value);

    if data.is_array() {
        serde_json::from_value(data.clone()).map_err(|e| {
            GatewayError::Api {
                status,
                message: format!("failed to parse list: {e}"),
            }
            .into()
        })
    } else {
        let single: T = serde_json::from_value(data.clone()).map_err(|e| GatewayError::Api {
            status,
            message: format!("failed to parse item: {e}"),
        })?;
        Ok(vec![single])
    }
}
