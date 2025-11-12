from pathlib import Path

import click

from toolfront.lib.config import get_api_credentials
from toolfront.lib.gateway import GatewayClient


@click.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--api-key", help="Gateway API key (overrides config)")
@click.option("--gateway-url", help="Gateway base URL (overrides config)")
@click.option("--name", help="Environment name (defaults to directory name)")
@click.option("--verify", is_flag=True, help="Wait and verify environment is accessible after deployment")
def deploy(path: Path, api_key: str | None, gateway_url: str | None, name: str | None, verify: bool):
    """Deploy markdown repository to Gateway"""
    try:
        gateway_url, api_key = get_api_credentials(api_key, gateway_url)
    except ValueError as e:
        raise click.ClickException(str(e)) from e

    dir_path = path if path.is_dir() else path.parent
    env_name = name or dir_path.name

    click.echo(f"Scanning {dir_path}...")
    client = GatewayClient(gateway_url, api_key)
    files = client.scan_markdown_files(dir_path)

    if not files:
        click.echo("Error: No markdown files found", err=True)
        return

    click.echo(f"Found {len(files)} file(s)")
    click.echo(f"\nDeploying '{click.style(env_name, bold=True)}'...")

    try:
        result = client.deploy_environment(env_name, files)

        click.echo("\n" + "─" * 80)
        click.echo(f"  Deployment ID:  {click.style(result.id, fg='green')}")
        if result.fly_url:
            click.echo(f"  URL:    {click.style(result.url, fg='blue', bold=True)}")
        if result.auth_token:
            click.echo(f"  Auth Token:     {result.auth_token}")
        click.echo("─" * 80)

        click.echo("\n✓ Deployment created. Use the URL above (ready immediately).")

        if verify and result.auth_token:
            verify_url = result.url
            if verify_url:
                click.echo("\nWaiting for environment to be ready...")

                def progress(attempt, max_attempts, error):
                    if attempt % 5 == 0:
                        click.echo(f"  Still waiting... ({attempt}/{max_attempts})")

                if client.verify_environment(verify_url, result.auth_token, progress_callback=progress):
                    click.echo(f"\n{click.style('✓', fg='green')} Environment is ready!")
                else:
                    click.echo(
                        f"\nVerification timed out. Environment may still be starting.\n"
                        f"Try accessing it directly: {verify_url}",
                        err=True,
                    )
    except RuntimeError as e:
        raise click.ClickException(str(e)) from e
