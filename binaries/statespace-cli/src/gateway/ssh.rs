use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
#[allow(dead_code)]
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
