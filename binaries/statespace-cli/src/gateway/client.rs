use crate::config::Credentials;
use crate::error::{GatewayError, Result};
use crate::gateway::auth::{DeviceCodeResponse, DeviceTokenResponse};
use crate::gateway::environments::{DeployResult, Environment, EnvironmentFile, UpsertResult};
use crate::gateway::organizations::Organization;
use crate::gateway::ssh::SshKey;
use crate::gateway::tokens::{Token, TokenCreateResult};
use base64::{Engine, engine::general_purpose::STANDARD as BASE64};
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

    pub(crate) fn base_url(&self) -> &str {
        &self.base_url
    }

    #[allow(dead_code)]
    pub(crate) fn api_key(&self) -> &str {
        &self.api_key
    }

    fn require_org_id(&self) -> Result<&str> {
        self.org_id
            .as_deref()
            .ok_or_else(|| GatewayError::MissingOrgId.into())
    }

    fn with_headers(&self, builder: reqwest::RequestBuilder) -> reqwest::RequestBuilder {
        let builder = builder.header("Authorization", self.auth_header());
        if let Some(ref org_id) = self.org_id {
            builder.header("X-Statespace-Org-Id", org_id)
        } else {
            builder
        }
    }

    pub(crate) fn scan_markdown_files(dir: &Path) -> Result<Vec<EnvironmentFile>> {
        let mut files = Vec::new();

        for path in collect_files(dir)? {
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

    pub(crate) async fn create_environment(
        &self,
        name: &str,
        files: Vec<EnvironmentFile>,
        visibility: crate::args::VisibilityArg,
    ) -> Result<DeployResult> {
        #[derive(Serialize)]
        struct Payload<'a> {
            name: &'a str,
            files: Vec<EnvironmentFile>,
            visibility: &'a str,
        }

        let visibility_str = match visibility {
            crate::args::VisibilityArg::Public => "public",
            crate::args::VisibilityArg::Private => "private",
        };

        let url = format!("{}/api/v1/environments", self.base_url);
        let resp = self
            .with_headers(self.http.post(&url))
            .json(&Payload {
                name,
                files,
                visibility: visibility_str,
            })
            .send()
            .await?;

        parse_api_response(resp).await
    }

    pub(crate) async fn list_environments(&self) -> Result<Vec<Environment>> {
        let url = format!("{}/api/v1/environments", self.base_url);
        let resp = self.with_headers(self.http.get(&url)).send().await?;

        parse_api_list_response(resp).await
    }

    pub(crate) async fn get_environment(&self, id_or_name: &str) -> Result<Environment> {
        let url = format!("{}/api/v1/environments/{}", self.base_url, id_or_name);
        let resp = self.with_headers(self.http.get(&url)).send().await?;

        parse_api_response(resp).await
    }

    pub(crate) async fn upsert_environment(
        &self,
        name: &str,
        files: Vec<EnvironmentFile>,
    ) -> Result<UpsertResult> {
        #[derive(Serialize)]
        struct Payload {
            files: Vec<EnvironmentFile>,
        }

        let url = format!(
            "{}/api/v1/environments/by-name/{}",
            self.base_url,
            urlencoding::encode(name)
        );
        let resp = self
            .with_headers(self.http.put(&url))
            .json(&Payload { files })
            .send()
            .await?;

        parse_api_response(resp).await
    }

    pub(crate) async fn delete_environment(&self, environment_id: &str) -> Result<()> {
        let url = format!("{}/api/v1/environments/{}", self.base_url, environment_id);
        let resp = self.with_headers(self.http.delete(&url)).send().await?;

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
                let wait = std::cmp::min(
                    VERIFY_BASE_DELAY_SECS * u64::from(attempt),
                    VERIFY_MAX_DELAY_SECS,
                );
                tokio::time::sleep(Duration::from_secs(wait)).await;
            }
        }
        Ok(false)
    }

    #[allow(clippy::items_after_statements)]
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
            .with_headers(self.http.post(&url))
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
            .with_headers(self.http.get(&url))
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
        let resp = self.with_headers(self.http.get(&url)).send().await?;

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
        #[allow(clippy::struct_field_names)]
        struct Payload<'a> {
            #[serde(skip_serializing_if = "Option::is_none")]
            new_name: Option<&'a str>,
            #[serde(skip_serializing_if = "Option::is_none")]
            new_scope: Option<String>,
            #[serde(skip_serializing_if = "Option::is_none")]
            new_allowed_environment_ids: Option<&'a [String]>,
            #[serde(skip_serializing_if = "Option::is_none")]
            new_expires_at: Option<&'a str>,
        }

        let url = format!("{}/api/v1/tokens/{}/rotate", self.base_url, token_id);
        let resp = self
            .with_headers(self.http.post(&url))
            .json(&Payload {
                new_name: name,
                new_scope: scope.map(|s| format!("environments:{s}")),
                new_allowed_environment_ids: environment_ids,
                new_expires_at: expires_at,
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
            .with_headers(self.http.delete(&url))
            .json(&Payload { reason })
            .send()
            .await?;

        check_api_response(resp).await
    }

    pub(crate) async fn list_organizations(&self) -> Result<Vec<Organization>> {
        let url = format!("{}/api/v1/user/organizations", self.base_url);
        let resp = self.with_headers(self.http.get(&url)).send().await?;
        parse_api_list_response(resp).await
    }

    pub(crate) async fn add_ssh_key(&self, name: &str, public_key: &str) -> Result<SshKey> {
        #[derive(Serialize)]
        struct Payload<'a> {
            name: &'a str,
            public_key: &'a str,
        }

        let url = format!("{}/api/v1/ssh-keys", self.base_url);
        let resp = self
            .with_headers(self.http.post(&url))
            .json(&Payload { name, public_key })
            .send()
            .await?;

        parse_api_response(resp).await
    }

    pub(crate) async fn list_ssh_keys(&self) -> Result<Vec<SshKey>> {
        let url = format!("{}/api/v1/ssh-keys", self.base_url);
        let resp = self.with_headers(self.http.get(&url)).send().await?;
        parse_api_list_response(resp).await
    }

    pub(crate) async fn remove_ssh_key(&self, fingerprint: &str) -> Result<()> {
        let url = format!(
            "{}/api/v1/ssh-keys/{}",
            self.base_url,
            urlencoding::encode(fingerprint)
        );
        let resp = self.with_headers(self.http.delete(&url)).send().await?;
        check_api_response(resp).await
    }
}

fn collect_files(dir: &Path) -> Result<Vec<std::path::PathBuf>> {
    let mut results = Vec::new();
    for entry in walkdir::WalkDir::new(dir) {
        let entry = entry
            .map_err(|e| crate::error::Error::cli(format!("Failed to walk directory: {e}")))?;
        if entry.file_type().is_file() {
            results.push(entry.into_path());
        }
    }
    Ok(results)
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
    Err(GatewayError::Api {
        status: status.as_u16(),
        message,
    }
    .into())
}

async fn parse_api_response<T: serde::de::DeserializeOwned>(resp: reqwest::Response) -> Result<T> {
    let status = resp.status();
    let text = resp
        .text()
        .await
        .unwrap_or_else(|e| format!("(failed to read body: {e})"));

    if !status.is_success() {
        let message = text.chars().take(512).collect();
        return Err(GatewayError::Api {
            status: status.as_u16(),
            message,
        }
        .into());
    }

    let status_code = status.as_u16();
    let value: Value = serde_json::from_str(&text).map_err(|e| GatewayError::Api {
        status: status_code,
        message: format!("invalid JSON: {e}"),
    })?;

    let data = value.get("data").unwrap_or(&value);

    serde_json::from_value(data.clone()).map_err(|e| {
        GatewayError::Api {
            status: status_code,
            message: format!("failed to parse response: {e}"),
        }
        .into()
    })
}

async fn parse_api_list_response<T: serde::de::DeserializeOwned>(
    resp: reqwest::Response,
) -> Result<Vec<T>> {
    let status = resp.status();
    let status_code = status.as_u16();
    let text = resp
        .text()
        .await
        .unwrap_or_else(|e| format!("(failed to read body: {e})"));

    if !status.is_success() {
        let message = text.chars().take(512).collect();
        return Err(GatewayError::Api {
            status: status_code,
            message,
        }
        .into());
    }

    let value: Value = serde_json::from_str(&text).map_err(|e| GatewayError::Api {
        status: status_code,
        message: format!("invalid JSON: {e}"),
    })?;

    let data = value.get("data").unwrap_or(&value);

    if data.is_array() {
        serde_json::from_value(data.clone()).map_err(|e| {
            GatewayError::Api {
                status: status_code,
                message: format!("failed to parse list: {e}"),
            }
            .into()
        })
    } else {
        let single: T = serde_json::from_value(data.clone()).map_err(|e| GatewayError::Api {
            status: status_code,
            message: format!("failed to parse item: {e}"),
        })?;
        Ok(vec![single])
    }
}

/// Unauthenticated client for RFC 8628 device authorization.
pub(crate) struct AuthClient {
    base_url: String,
    http: Client,
}

impl AuthClient {
    pub(crate) fn with_url(base_url: &str) -> Result<Self> {
        let http = Client::builder()
            .user_agent(USER_AGENT)
            .timeout(Duration::from_secs(30))
            .build()
            .map_err(|e| GatewayError::ClientBuild(e.to_string()))?;

        Ok(Self {
            base_url: base_url.to_string(),
            http,
        })
    }

    pub(crate) async fn request_device_code(&self) -> Result<DeviceCodeResponse> {
        let url = format!("{}/api/v1/auth/device/code", self.base_url);
        let resp = self.http.post(&url).send().await?;
        parse_api_response(resp).await
    }

    pub(crate) async fn poll_device_token(&self, device_code: &str) -> Result<DeviceTokenResponse> {
        #[derive(Serialize)]
        struct Payload<'a> {
            device_code: &'a str,
        }

        let url = format!("{}/api/v1/auth/device/token", self.base_url);
        let resp = self
            .http
            .post(&url)
            .json(&Payload { device_code })
            .send()
            .await?;

        parse_api_response(resp).await
    }

    pub(crate) async fn exchange_token(
        &self,
        access_token: &str,
    ) -> Result<crate::gateway::auth::ExchangeTokenResponse> {
        let url = format!("{}/api/v1/cli/tokens:exchange", self.base_url);
        let resp = self
            .http
            .post(&url)
            .header("Authorization", format!("Bearer {access_token}"))
            .send()
            .await?;

        parse_api_response(resp).await
    }
}
