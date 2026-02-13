#![allow(dead_code)]

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize)]
pub(crate) struct EnvironmentFile {
    pub path: String,
    pub content: String,
    pub checksum: String,
}

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct DeployResult {
    pub id: String,
    pub auth_token: Option<String>,
    pub url: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct UpsertResult {
    pub created: bool,
    pub id: String,
    pub name: String,
    pub url: Option<String>,
    pub auth_token: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct Environment {
    pub id: String,
    pub name: String,
    pub status: String,
    pub url: Option<String>,
    pub created_at: String,
    pub auth_token: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct Token {
    pub id: String,
    pub name: String,
    pub scope: String,
    pub created_at: String,
    #[serde(default)]
    pub is_active: bool,
    pub expires_at: Option<String>,
    pub last_used_at: Option<String>,
    #[serde(default)]
    pub usage_count: u64,
    pub allowed_environments: Option<Vec<String>>,
    pub revoked_at: Option<String>,
    pub revoked_by: Option<String>,
    pub revocation_reason: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct TokenCreateResult {
    pub id: String,
    pub name: String,
    pub scope: String,
    pub token: String,
    pub created_at: String,
    pub expires_at: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct DeviceCodeResponse {
    pub device_code: String,
    pub user_code: String,
    pub verification_url: String,
    #[serde(default = "default_interval")]
    pub interval: u64,
    #[serde(default = "default_expires_in")]
    pub expires_in: u64,
}

fn default_interval() -> u64 {
    5
}

fn default_expires_in() -> u64 {
    900
}

#[derive(Debug, Clone, Deserialize)]
#[serde(tag = "status", rename_all = "snake_case")]
pub(crate) enum DeviceTokenResponse {
    Pending,
    Authorized(AuthorizedUser),
    Expired,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub(crate) struct AuthorizedUser {
    pub access_token: String,
    pub email: String,
    pub name: Option<String>,
    pub user_id: String,
    pub expires_at: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct ExchangeTokenResponse {
    pub api_key: String,
    pub key_prefix: String,
    pub organization_id: String,
    pub expires_at: Option<String>,
    pub name: String,
}

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct Organization {
    pub id: String,
    pub name: String,
    pub tier: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct SshConnectionConfig {
    pub sprite_name: String,
    pub sprites_api_url: String,
    pub sprites_token: String,
}

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct SshKey {
    pub id: String,
    pub name: String,
    pub fingerprint: String,
    pub created_at: String,
}
