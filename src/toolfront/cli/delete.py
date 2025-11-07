import click

from toolfront.lib.gateway import GatewayClient


@click.command()
@click.argument("deployment_id")
@click.option("--api-key", envvar="TOOLFRONT_API_KEY", required=True, help="Gateway API key")
@click.option(
    "--gateway-url",
    default="https://api.toolfront.ai",
    envvar="TOOLFRONT_GATEWAY_URL",
    help="Gateway base URL",
)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def delete(deployment_id: str, api_key: str, gateway_url: str, yes: bool):
    """Delete a deployment by ID"""
    if not yes and not click.confirm(f"Are you sure you want to delete deployment {deployment_id}?"):
        click.echo("Cancelled")
        return

    try:
        client = GatewayClient(gateway_url, api_key)
        client.delete_environment(deployment_id)
        click.echo(f"✅ Deployment {deployment_id} deleted successfully")

    except RuntimeError as e:
        raise click.ClickException(str(e)) from e
