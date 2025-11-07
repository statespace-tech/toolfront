import click

from toolfront.lib.gateway import GatewayClient


@click.command()
@click.option("--api-key", envvar="TOOLFRONT_API_KEY", required=True, help="Gateway API key")
@click.option(
    "--gateway-url",
    default="https://api.toolfront.ai",
    envvar="TOOLFRONT_GATEWAY_URL",
    help="Gateway base URL",
)
def list_deployments(api_key: str, gateway_url: str):
    """List all deployments"""
    try:
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
