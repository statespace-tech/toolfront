//! SSH tunnel to sprite environments via Sprites WebSocket proxy.

use crate::args::{AppSshArgs, AppSshProxyArgs};
use crate::error::{Error, Result};
use crate::gateway::GatewayClient;
use futures_util::{SinkExt, StreamExt};
use serde::{Deserialize, Serialize};
use std::process::Stdio;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::process::Command;
use tokio_tungstenite::{
    connect_async,
    tungstenite::{http::Request, Message},
};

#[derive(Debug, Serialize)]
struct ProxyInit {
    host: String,
    port: u16,
}

#[derive(Debug, Deserialize)]
struct ProxyStatus {
    status: String,
    #[allow(dead_code)]
    target: Option<String>,
}

/// Spawns SSH client with ProxyCommand pointing to `ssh-proxy` subcommand.
pub(crate) async fn run_ssh(args: AppSshArgs, _gateway: GatewayClient) -> Result<()> {
    let exe = std::env::current_exe()
        .map_err(|e| Error::cli(format!("Failed to get executable path: {e}")))?;

    let proxy_cmd = format!(
        "{} app ssh-proxy {} --port {}",
        exe.display(),
        args.app,
        args.port
    );

    let status = Command::new("ssh")
        .arg("-o")
        .arg(format!("ProxyCommand={proxy_cmd}"))
        .arg("-o")
        .arg("StrictHostKeyChecking=no")
        .arg("-o")
        .arg("UserKnownHostsFile=/dev/null")
        .arg(format!("{}@sprite", args.user))
        .stdin(Stdio::inherit())
        .stdout(Stdio::inherit())
        .stderr(Stdio::inherit())
        .status()
        .await
        .map_err(|e| Error::cli(format!("Failed to spawn SSH: {e}")))?;

    if !status.success() {
        if let Some(code) = status.code() {
            std::process::exit(code);
        }
    }

    Ok(())
}

/// Raw TCP proxy over WebSocket - used by SSH's ProxyCommand.
///
/// Protocol: connect to `wss://api.sprites.dev/v1/sprites/{name}/proxy`,
/// send `{"host":"localhost","port":22}`, receive status, then relay stdin/stdout.
pub(crate) async fn run_ssh_proxy(args: AppSshProxyArgs, gateway: GatewayClient) -> Result<()> {
    let config = gateway.get_ssh_config(&args.app).await?;

    let ws_url = format!(
        "{}/v1/sprites/{}/proxy",
        config.sprites_api_url.replace("https://", "wss://"),
        config.sprite_name
    );

    let request = Request::builder()
        .uri(&ws_url)
        .header("Authorization", format!("Bearer {}", config.sprites_token))
        .header("Host", "api.sprites.dev")
        .header("Connection", "Upgrade")
        .header("Upgrade", "websocket")
        .header("Sec-WebSocket-Version", "13")
        .header(
            "Sec-WebSocket-Key",
            tokio_tungstenite::tungstenite::handshake::client::generate_key(),
        )
        .body(())
        .map_err(|e| Error::cli(format!("Failed to build WebSocket request: {e}")))?;

    let (ws_stream, _response) = connect_async(request)
        .await
        .map_err(|e| Error::cli(format!("Failed to connect to Sprites proxy: {e}")))?;

    let (mut ws_write, mut ws_read) = ws_stream.split();

    let init = ProxyInit {
        host: args.host.clone(),
        port: args.port,
    };
    let init_json =
        serde_json::to_string(&init).map_err(|e| Error::cli(format!("JSON error: {e}")))?;

    ws_write
        .send(Message::Text(init_json.into()))
        .await
        .map_err(|e| Error::cli(format!("Failed to send init: {e}")))?;

    let status_msg = ws_read
        .next()
        .await
        .ok_or_else(|| Error::cli("Connection closed before status"))?
        .map_err(|e| Error::cli(format!("Failed to read status: {e}")))?;

    match &status_msg {
        Message::Text(text) => {
            let status: ProxyStatus = serde_json::from_str(text)
                .map_err(|e| Error::cli(format!("Invalid status JSON: {e}")))?;

            if status.status != "connected" {
                return Err(Error::cli(format!(
                    "Proxy connection failed: {}",
                    status.status
                )));
            }
        }
        Message::Binary(data) => {
            return Err(Error::cli(format!(
                "Expected text status, got binary ({} bytes): {:?}",
                data.len(),
                String::from_utf8_lossy(&data[..data.len().min(100)])
            )));
        }
        Message::Close(frame) => {
            return Err(Error::cli(format!("Connection closed: {:?}", frame)));
        }
        other => {
            return Err(Error::cli(format!("Unexpected message type: {:?}", other)));
        }
    }

    let mut stdin = tokio::io::stdin();
    let mut stdout = tokio::io::stdout();
    let mut stdin_buf = vec![0u8; 8192];

    loop {
        tokio::select! {
            result = stdin.read(&mut stdin_buf) => {
                match result {
                    Ok(0) => {
                        let _ = ws_write.close().await;
                        break;
                    }
                    Ok(n) => {
                        let data = stdin_buf[..n].to_vec();
                        if ws_write.send(Message::Binary(data.into())).await.is_err() {
                            break;
                        }
                    }
                    Err(_) => break,
                }
            }

            msg = ws_read.next() => {
                match msg {
                    Some(Ok(Message::Binary(data))) => {
                        if stdout.write_all(&data).await.is_err() {
                            break;
                        }
                        let _ = stdout.flush().await;
                    }
                    Some(Ok(Message::Text(text))) => {
                        if stdout.write_all(text.as_bytes()).await.is_err() {
                            break;
                        }
                        let _ = stdout.flush().await;
                    }
                    Some(Ok(Message::Close(_))) | None => {
                        break;
                    }
                    Some(Ok(_)) => {}
                    Some(Err(_)) => break,
                }
            }
        }
    }

    Ok(())
}
