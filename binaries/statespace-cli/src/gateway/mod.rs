//! Gateway API client.

#![allow(dead_code)] // Gateway client has methods for future commands

mod client;
mod types;

pub(crate) use client::{AuthClient, GatewayClient};
pub(crate) use types::{AuthorizedUser, DeviceTokenResponse, ExchangeTokenResponse};
