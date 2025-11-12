import click

from toolfront.lib.config import get_api_credentials
from toolfront.lib.gateway import GatewayClient


@click.command()
@click.option("--api-key", help="Gateway API key (overrides config)")
@click.option("--gateway-url", help="Gateway base URL (overrides config)")
def list_deployments(api_key: str | None, gateway_url: str | None):
    """List all deployments"""
    try:
        gateway_url, api_key = get_api_credentials(api_key, gateway_url)
        client = GatewayClient(gateway_url, api_key)
        envs = client.list_environments()

        if not envs:
            click.echo("No deployments found")
            return

        click.echo(f"📦 {len(envs)} deployment(s)\n")

        click.echo(f"{'NAME':<30} {'STATUS':<12} {'ID':<38} {'URL'}")
        click.echo("─" * 120)

        for env in envs:
            status_emoji = "✅" if env.status == "running" else "⏳" if env.status == "pending" else "❌"
            status_display = f"{status_emoji} {env.status}"
            name_display = click.style(env.name, bold=True, fg="cyan")
            id_display = click.style(env.id[:36], dim=True)
            url_display = env.url or "-"

            click.echo(f"{name_display:<38} {status_display:<20} {id_display:<38} {url_display}")

    except RuntimeError as e:
        raise click.ClickException(str(e)) from e
