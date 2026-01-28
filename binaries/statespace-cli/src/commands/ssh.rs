//! SSH tunnel to environments via WebSocket proxy.

use crate::args::{AppSshArgs, AppSshProxyArgs};
use crate::config::resolve_credentials;
use crate::error::{Error, Result};
use crate::gateway::GatewayClient;
use futures_util::{SinkExt, StreamExt};
use std::process::Stdio;
use std::time::Duration;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::process::Command;
use tokio_tungstenite::{connect_async, tungstenite::Message};

pub(crate) async fn run_ssh(args: AppSshArgs, gateway: GatewayClient) -> Result<()> {
    let exe = std::env::current_exe()
        .map_err(|e| Error::cli(format!("Failed to get executable path: {e}")))?;

    let proxy_cmd = format!(
        "env STATESPACE_API_URL={} STATESPACE_API_KEY={} {} app ssh-proxy {} --port {}",
        gateway.base_url(),
        gateway.api_key(),
        exe.display(),
        args.app,
        args.port
    );

    let status = Command::new("ssh")
        .args(["-o", &format!("ProxyCommand={proxy_cmd}")])
        .args(["-o", "StrictHostKeyChecking=no"])
        .args(["-o", "UserKnownHostsFile=/dev/null"])
        .arg(format!("{}@env", args.user))
        .stdin(Stdio::inherit())
        .stdout(Stdio::inherit())
        .stderr(Stdio::inherit())
        .status()
        .await
        .map_err(|e| Error::cli(format!("Failed to spawn SSH: {e}")))?;

    if !status.success()
        && let Some(code) = status.code()
    {
        std::process::exit(code);
    }

    Ok(())
}

fn normalize_app_name(app: &str) -> &str {
    app.strip_suffix(".statespace").unwrap_or(app)
}

pub(crate) async fn run_ssh_proxy(args: AppSshProxyArgs) -> Result<()> {
    let creds = resolve_credentials(None, None, None)?;
    let gateway = GatewayClient::new(creds)?;
    let app_name = normalize_app_name(&args.app);

    let env = gateway.get_environment(app_name).await?;

    let env_url = env.url.ok_or_else(|| {
        Error::cli(format!(
            "Environment '{}' has no URL - is it running?",
            args.app
        ))
    })?;

    let auth_token = env
        .auth_token
        .ok_or_else(|| Error::cli(format!("Environment '{}' has no auth token", args.app)))?;

    let ws_url = env_url.replace("https://", "wss://") + "/ssh";
    let host = ws_url
        .replace("wss://", "")
        .split('/')
        .next()
        .unwrap_or("")
        .to_string();

    let request = tokio_tungstenite::tungstenite::http::Request::builder()
        .uri(&ws_url)
        .header("Authorization", format!("Bearer {auth_token}"))
        .header("Sec-WebSocket-Version", "13")
        .header(
            "Sec-WebSocket-Key",
            tokio_tungstenite::tungstenite::handshake::client::generate_key(),
        )
        .header("Connection", "Upgrade")
        .header("Upgrade", "websocket")
        .header("Host", host)
        .body(())
        .map_err(|e| Error::cli(format!("Failed to build WebSocket request: {e}")))?;

    let (ws_stream, _) = connect_async(request)
        .await
        .map_err(|e| Error::cli(format!("Failed to connect to SSH endpoint: {e}")))?;

    proxy_stdio_to_websocket(ws_stream).await
}

async fn proxy_stdio_to_websocket<S>(ws_stream: S) -> Result<()>
where
    S: futures_util::Stream<
            Item = std::result::Result<Message, tokio_tungstenite::tungstenite::Error>,
        > + futures_util::Sink<Message, Error = tokio_tungstenite::tungstenite::Error>
        + Unpin,
{
    let (mut ws_write, mut ws_read) = ws_stream.split();

    let mut stdin = tokio::io::stdin();
    let mut stdout = tokio::io::stdout();
    let mut buf = vec![0u8; 8192];

    let mut ping_interval = tokio::time::interval(Duration::from_secs(20));
    ping_interval.tick().await;

    loop {
        tokio::select! {
            result = stdin.read(&mut buf) => {
                match result {
                    Ok(0) => { let _ = ws_write.close().await; break; }
                    Ok(n) => {
                        if ws_write.send(Message::Binary(buf[..n].to_vec().into())).await.is_err() {
                            break;
                        }
                    }
                    Err(_) => break,
                }
            }

            msg = ws_read.next() => {
                match msg {
                    Some(Ok(Message::Binary(data))) => {
                        if stdout.write_all(&data).await.is_err() { break; }
                        let _ = stdout.flush().await;
                    }
                    Some(Ok(Message::Text(text))) => {
                        if stdout.write_all(text.as_bytes()).await.is_err() { break; }
                        let _ = stdout.flush().await;
                    }
                    Some(Ok(Message::Close(_)) | Err(_)) | None => break,
                    Some(Ok(_)) => {}
                }
            }

            _ = ping_interval.tick() => {
                if ws_write.send(Message::Ping(vec![].into())).await.is_err() {
                    break;
                }
            }
        }
    }

    Ok(())
}
