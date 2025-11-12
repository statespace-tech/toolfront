import click

from toolfront.lib.config import get_api_credentials
from toolfront.lib.gateway import GatewayClient


@click.command()
@click.argument("deployment_id")
@click.option("--api-key", help="Gateway API key (overrides config)")
@click.option("--gateway-url", help="Gateway base URL (overrides config)")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def delete(deployment_id: str, api_key: str | None, gateway_url: str | None, yes: bool):
    """Delete a deployment by ID"""
    if not yes and not click.confirm(f"Are you sure you want to delete deployment {deployment_id}?"):
        click.echo("Cancelled")
        return

    try:
        gateway_url, api_key = get_api_credentials(api_key, gateway_url)
        client = GatewayClient(gateway_url, api_key)
        client.delete_environment(deployment_id)
        click.echo(f"✅ Deployment {deployment_id} deleted successfully")

    except RuntimeError as e:
        raise click.ClickException(str(e)) from e
