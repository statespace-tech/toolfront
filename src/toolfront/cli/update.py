from pathlib import Path

import click

from toolfront.lib.config import get_api_credentials
from toolfront.lib.gateway import GatewayClient


@click.command()
@click.argument("deployment_id")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--api-key", help="Gateway API key (overrides config)")
@click.option("--gateway-url", help="Gateway base URL (overrides config)")
def update(deployment_id: str, path: Path, api_key: str | None, gateway_url: str | None):
    """Update deployment with new markdown files"""
    try:
        gateway_url, api_key = get_api_credentials(api_key, gateway_url)
    except ValueError as e:
        raise click.ClickException(str(e)) from e

    dir_path = path if path.is_dir() else path.parent

    click.echo(f"Scanning {dir_path}...")
    client = GatewayClient(gateway_url, api_key)
    files = client.scan_markdown_files(dir_path)

    if not files:
        click.echo("Error: No markdown files found", err=True)
        return

    click.echo(f"Found {len(files)} file(s)")
    click.echo(f"\nUpdating deployment {click.style(deployment_id, bold=True)}...")

    try:
        client.update_environment(deployment_id, files)

        click.echo("\n" + "─" * 80)
        click.echo(f"  {click.style('✓', fg='green')} Deployment updated successfully")
        click.echo("  Files uploaded and search index updated")
        click.echo("─" * 80)

    except RuntimeError as e:
        raise click.ClickException(str(e)) from e
