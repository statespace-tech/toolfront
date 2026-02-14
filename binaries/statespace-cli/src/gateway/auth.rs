use serde::{Deserialize, Serialize};

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
#[allow(dead_code)]
pub(crate) struct ExchangeTokenResponse {
    pub api_key: String,
    pub key_prefix: String,
    pub organization_id: String,
    pub expires_at: Option<String>,
    pub name: String,
}
