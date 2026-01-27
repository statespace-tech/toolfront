//! Gateway API client for Statespace.

use crate::config::Credentials;
use crate::error::{GatewayError, Result};
use reqwest::Client;
use serde::{Deserialize, Serialize};

const DEFAULT_AUTH_URL: &str = "https://auth.statespace.com";

#[derive(Debug, Clone)]
pub(crate) struct GatewayClient {
    client: Client,
    base_url: String,
    api_key: String,
    org_id: Option<String>,
}

impl GatewayClient {
    pub(crate) fn new(credentials: Credentials) -> Result<Self> {
        let client = Client::builder()
            .build()
            .map_err(|e| GatewayError::Http(e.to_string()))?;

        Ok(Self {
            client,
            base_url: credentials.api_url,
            api_key: credentials.api_key,
            org_id: credentials.org_id,
        })
    }

    async fn get<T: for<'de> Deserialize<'de>>(&self, path: &str) -> Result<T> {
        let url = format!("{}{}", self.base_url, path);
        let mut req = self.client.get(&url).bearer_auth(&self.api_key);

        if let Some(org_id) = &self.org_id {
            req = req.header("X-Organization-ID", org_id);
        }

        let resp = req.send().await.map_err(GatewayError::from)?;
        self.handle_response(resp).await
    }

    async fn post<T: for<'de> Deserialize<'de>, B: Serialize>(
        &self,
        path: &str,
        body: &B,
    ) -> Result<T> {
        let url = format!("{}{}", self.base_url, path);
        let mut req = self.client.post(&url).bearer_auth(&self.api_key).json(body);

        if let Some(org_id) = &self.org_id {
            req = req.header("X-Organization-ID", org_id);
        }

        let resp = req.send().await.map_err(GatewayError::from)?;
        self.handle_response(resp).await
    }

    async fn delete(&self, path: &str) -> Result<()> {
        let url = format!("{}{}", self.base_url, path);
        let mut req = self.client.delete(&url).bearer_auth(&self.api_key);

        if let Some(org_id) = &self.org_id {
            req = req.header("X-Organization-ID", org_id);
        }

        let resp = req.send().await.map_err(GatewayError::from)?;
        let status = resp.status();

        if status.is_success() || status.as_u16() == 204 {
            return Ok(());
        }

        if status.as_u16() == 401 {
            return Err(GatewayError::Unauthorized.into());
        }

        if status.as_u16() == 404 {
            return Err(GatewayError::NotFound("Resource not found".into()).into());
        }

        let text = resp.text().await.unwrap_or_default();
        Err(GatewayError::Api {
            status: status.as_u16(),
            message: text,
        }
        .into())
    }

    async fn handle_response<T: for<'de> Deserialize<'de>>(
        &self,
        resp: reqwest::Response,
    ) -> Result<T> {
        let status = resp.status();

        if status.is_success() {
            return resp
                .json()
                .await
                .map_err(|e| GatewayError::Parse(e.to_string()).into());
        }

        if status.as_u16() == 401 {
            return Err(GatewayError::Unauthorized.into());
        }

        if status.as_u16() == 404 {
            return Err(GatewayError::NotFound("Resource not found".into()).into());
        }

        let text = resp.text().await.unwrap_or_default();
        Err(GatewayError::Api {
            status: status.as_u16(),
            message: text,
        }
        .into())
    }

    pub(crate) async fn list_organizations(&self) -> Result<Vec<Organization>> {
        let resp: OrganizationsResponse = self.get("/api/v1/organizations").await?;
        Ok(resp.organizations)
    }

    #[allow(dead_code)]
    pub(crate) async fn get_environment(&self, id: &str) -> Result<Environment> {
        self.get(&format!("/api/v1/environments/{id}")).await
    }

    pub(crate) async fn get_ssh_config(&self, app: &str) -> Result<SshConfig> {
        self.get(&format!("/api/v1/environments/{app}/ssh")).await
    }

    pub(crate) async fn list_ssh_keys(&self) -> Result<Vec<SshKey>> {
        let resp: SshKeysResponse = self.get("/api/v1/users/me/ssh-keys").await?;
        Ok(resp.ssh_keys)
    }

    pub(crate) async fn add_ssh_key(&self, name: &str, public_key: &str) -> Result<SshKey> {
        let body = AddSshKeyRequest {
            name: name.to_string(),
            public_key: public_key.to_string(),
        };
        self.post("/api/v1/users/me/ssh-keys", &body).await
    }

    pub(crate) async fn remove_ssh_key(&self, id: &str) -> Result<()> {
        self.delete(&format!("/api/v1/users/me/ssh-keys/{id}"))
            .await
    }
}

#[derive(Debug, Deserialize)]
struct OrganizationsResponse {
    organizations: Vec<Organization>,
}

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct Organization {
    pub id: String,
    pub name: String,
    pub tier: Option<String>,
}

#[allow(dead_code)]
#[derive(Debug, Deserialize)]
pub(crate) struct Environment {
    pub id: String,
    pub name: String,
    pub url: Option<String>,
    pub status: String,
    pub auth_token: Option<String>,
}

#[derive(Debug, Deserialize)]
pub(crate) struct SshConfig {
    pub sprites_api_url: String,
    pub sprite_name: String,
    pub sprites_token: String,
}

#[derive(Debug, Deserialize)]
struct SshKeysResponse {
    ssh_keys: Vec<SshKey>,
}

#[derive(Debug, Deserialize)]
pub(crate) struct SshKey {
    pub id: String,
    pub name: String,
    pub fingerprint: String,
    pub created_at: String,
}

#[derive(Debug, Serialize)]
struct AddSshKeyRequest {
    name: String,
    public_key: String,
}

#[derive(Debug, Clone)]
pub(crate) struct AuthClient {
    client: Client,
    auth_url: String,
    api_url: String,
}

impl AuthClient {
    pub(crate) fn with_url(api_url: &str) -> Result<Self> {
        let client = Client::builder()
            .build()
            .map_err(|e| GatewayError::Http(e.to_string()))?;

        Ok(Self {
            client,
            auth_url: DEFAULT_AUTH_URL.to_string(),
            api_url: api_url.to_string(),
        })
    }

    pub(crate) async fn request_device_code(&self) -> Result<DeviceCodeResponse> {
        let url = format!("{}/oauth/device/code", self.auth_url);

        let resp = self
            .client
            .post(&url)
            .form(&[
                ("client_id", "statespace-cli"),
                ("scope", "openid profile email"),
            ])
            .send()
            .await
            .map_err(GatewayError::from)?;

        if !resp.status().is_success() {
            let text = resp.text().await.unwrap_or_default();
            return Err(GatewayError::Api {
                status: 400,
                message: text,
            }
            .into());
        }

        resp.json()
            .await
            .map_err(|e| GatewayError::Parse(e.to_string()).into())
    }

    pub(crate) async fn poll_device_token(&self, device_code: &str) -> Result<DeviceTokenResponse> {
        let url = format!("{}/oauth/token", self.auth_url);

        let resp = self
            .client
            .post(&url)
            .form(&[
                ("client_id", "statespace-cli"),
                ("grant_type", "urn:ietf:params:oauth:grant-type:device_code"),
                ("device_code", device_code),
            ])
            .send()
            .await
            .map_err(GatewayError::from)?;

        if resp.status().is_success() {
            let auth: AuthorizedUser = resp
                .json()
                .await
                .map_err(|e| GatewayError::Parse(e.to_string()))?;
            return Ok(DeviceTokenResponse::Authorized(auth));
        }

        let text = resp.text().await.unwrap_or_default();

        if text.contains("authorization_pending") || text.contains("slow_down") {
            return Ok(DeviceTokenResponse::Pending);
        }

        if text.contains("expired_token") || text.contains("access_denied") {
            return Ok(DeviceTokenResponse::Expired);
        }

        Err(GatewayError::Api {
            status: 400,
            message: text,
        }
        .into())
    }

    pub(crate) async fn exchange_token(&self, access_token: &str) -> Result<ExchangeTokenResponse> {
        let url = format!("{}/api/v1/auth/exchange", self.api_url);

        let resp = self
            .client
            .post(&url)
            .bearer_auth(access_token)
            .send()
            .await
            .map_err(GatewayError::from)?;

        if !resp.status().is_success() {
            let text = resp.text().await.unwrap_or_default();
            return Err(GatewayError::Api {
                status: 400,
                message: text,
            }
            .into());
        }

        resp.json()
            .await
            .map_err(|e| GatewayError::Parse(e.to_string()).into())
    }
}

#[derive(Debug, Deserialize)]
pub(crate) struct DeviceCodeResponse {
    pub device_code: String,
    pub user_code: String,
    pub verification_url: String,
    pub expires_in: u64,
    pub interval: u64,
}

#[derive(Debug)]
pub(crate) enum DeviceTokenResponse {
    Pending,
    Authorized(AuthorizedUser),
    Expired,
}

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct AuthorizedUser {
    pub access_token: String,
    pub email: String,
    pub name: Option<String>,
    pub user_id: String,
    pub expires_at: Option<String>,
}

#[derive(Debug, Deserialize)]
pub(crate) struct ExchangeTokenResponse {
    pub api_key: String,
    pub organization_id: String,
    pub expires_at: Option<String>,
}
