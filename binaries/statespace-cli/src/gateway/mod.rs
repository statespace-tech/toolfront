//! Gateway API client

mod client;
mod types;

pub(crate) use client::{AuthClient, GatewayClient};
pub(crate) use types::{AuthorizedUser, DeviceTokenResponse, UpsertResult};
