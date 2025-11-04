from pathlib import Path

import click

from toolfront.lib.gateway import GatewayClient


@click.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--api-key", envvar="TOOLFRONT_API_KEY", required=True, help="Gateway API key")
@click.option(
    "--gateway-url",
    default="https://toolfront-gateway-staging.fly.dev",
    envvar="TOOLFRONT_GATEWAY_URL",
    help="Gateway base URL",
)
@click.option("--name", help="Environment name (defaults to directory name)")
@click.option("--verify/--no-verify", default=True, help="Verify environment is accessible after deployment")
def deploy(path: Path, api_key: str, gateway_url: str, name: str | None, verify: bool):
    """Deploy markdown repository to Gateway"""
    dir_path = path if path.is_dir() else path.parent
    env_name = name or dir_path.name

    click.echo(f"🔍 Scanning markdown files in {dir_path}...")
    client = GatewayClient(gateway_url, api_key)
    files = client.scan_markdown_files(dir_path)

    if not files:
        click.echo("⚠️  No markdown files found", err=True)
        return

    click.echo(f"📦 Found {len(files)} markdown file(s)")
    click.echo(f"🚀 Deploying environment '{env_name}'...")

    try:
        result = client.deploy_environment(env_name, files)
        click.echo(f"✅ Environment created: {result.id}")
        if result.url:
            click.echo(f"   Cloudflare URL: {result.url}")
        if result.fly_url:
            click.echo(f"   Fly URL: {result.fly_url}")
        if result.auth_token:
            click.echo(f"   Auth Token: {result.auth_token}")

        if verify and result.auth_token:
            verify_url = result.fly_url or result.url
            if verify_url:
                click.echo("\n⏳ Verifying environment...")
                if client.verify_environment(verify_url, result.auth_token):
                    click.echo("✅ Environment is ready!")
                else:
                    click.echo("⚠️  Verification timed out (environment may still be starting)", err=True)
    except RuntimeError as e:
        raise click.ClickException(str(e)) from e
