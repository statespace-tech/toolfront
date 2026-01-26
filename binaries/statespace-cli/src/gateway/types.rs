//! Gateway API types.

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
    pub fly_url: Option<String>,
}

/// Response from `PUT /api/v1/environments/by-name/{name}`.
///
/// Upsert semantics: creates if not exists, updates if exists.
#[derive(Debug, Clone, Deserialize)]
pub(crate) struct UpsertResult {
    /// Whether a new environment was created (false = updated existing)
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
    #[allow(dead_code)]
    pub fly_url: Option<String>,
    #[allow(dead_code)]
    pub created_at: String,
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

/// Response from `POST /api/v1/auth/device/code` (RFC 8628).
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

/// Response from `POST /api/v1/auth/device/token` polling endpoint.
#[derive(Debug, Clone, Deserialize)]
#[serde(tag = "status", rename_all = "snake_case")]
pub(crate) enum DeviceTokenResponse {
    Pending,
    Authorized(AuthorizedUser),
    Expired,
}

/// User info returned after successful device authorization.
#[derive(Debug, Clone, Deserialize, Serialize)]
pub(crate) struct AuthorizedUser {
    pub access_token: String,
    pub email: String,
    pub name: Option<String>,
    pub user_id: String,
    pub expires_at: Option<String>,
}

/// Response from `POST /api/v1/cli/tokens:exchange`.
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

/// SSH connection configuration for sprites
#[derive(Debug, Clone, Deserialize)]
pub(crate) struct SshConnectionConfig {
    /// Sprite name (e.g., env-{uuid})
    pub sprite_name: String,
    /// Sprites API URL (e.g., https://api.sprites.dev)
    pub sprites_api_url: String,
    /// Sprites API token for authentication
    pub sprites_token: String,
}

/// Organization SSH key
#[derive(Debug, Clone, Deserialize)]
pub(crate) struct SshKey {
    pub id: String,
    pub name: String,
    pub fingerprint: String,
    pub created_at: String,
}
