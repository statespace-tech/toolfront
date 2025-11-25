from datetime import UTC, datetime
from typing import Any

import click

from toolfront.lib.config import get_api_credentials
from toolfront.lib.gateway import GatewayClient


def get_client(api_key: str | None, gateway_url: str | None, org_id: str | None = None) -> GatewayClient:
    """Helper to initialize GatewayClient with error handling."""
    try:
        url, key, org = get_api_credentials(api_key, gateway_url, org_id)
        return GatewayClient(url, key, org)
    except ValueError as e:
        raise click.ClickException(str(e)) from e


def format_relative_time(iso_timestamp: str | None) -> str:
    """Format ISO timestamp to relative time string."""
    if not iso_timestamp:
        return "never"

    try:
        dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        now = datetime.now(UTC)
        delta = now - dt

        if delta.days > 0:
            return f"{delta.days}d ago"
        if delta.seconds >= 3600:
            return f"{delta.seconds // 3600}h ago"
        if delta.seconds >= 60:
            return f"{delta.seconds // 60}m ago"
        return "just now"
    except ValueError:
        return iso_timestamp


def print_kv(key: str, value: Any, color: str | None = None) -> None:
    """Print Key-Value pair if value is present."""
    if value is None or value == "":
        return

    val_str = str(value)
    if color:
        val_str = click.style(val_str, fg=color)

    click.echo(f"  {key:<16} {val_str}")


@click.group()
def tokens():
    """Manage Personal Access Tokens"""
    pass


@tokens.command()
@click.argument("name")
@click.option("--api-key", help="Gateway API key (overrides config)")
@click.option("--gateway-url", help="Gateway base URL (overrides config)")
@click.option("--org-id", help="Organization ID (overrides config)")
@click.option("--scope", type=click.Choice(["read", "execute", "admin"]), default="execute", help="Token scope")
@click.option("--env", "environment_ids", multiple=True, help="Restrict to specific environment IDs")
@click.option("--expires", help="Expiration date (ISO 8601 format)")
def create(
    name: str,
    api_key: str | None,
    gateway_url: str | None,
    org_id: str | None,
    scope: str,
    environment_ids: tuple[str, ...],
    expires: str | None,
):
    """Create a new Personal Access Token"""
    client = get_client(api_key, gateway_url, org_id)

    click.echo(f"Creating token '{click.style(name, bold=True)}'...")

    try:
        result = client.create_token(
            name=name,
            scope=scope,
            environment_ids=list(environment_ids) if environment_ids else None,
            expires_at=expires,
        )

        click.echo("\n" + "=" * 80)
        print_kv("Token ID:", result["id"], color="green")
        print_kv("Name:", result["name"])
        print_kv("Scope:", result["scope"])
        print_kv("Created:", result["created_at"])
        print_kv("Expires:", result.get("expires_at"))

        click.echo("\n" + "─" * 80)
        click.echo(f"  {click.style('Token (save this - shown only once):', fg='yellow', bold=True)}")
        click.echo(f"  {click.style(result['token'], fg='cyan', bold=True)}")
        click.echo("=" * 80)
        click.echo("\n✓ Token created successfully")

    except Exception as e:
        raise click.ClickException(f"Failed to create token: {e}") from e


@tokens.command(name="list")
@click.option("--api-key", help="Gateway API key (overrides config)")
@click.option("--gateway-url", help="Gateway base URL (overrides config)")
@click.option("--org-id", help="Organization ID (overrides config)")
@click.option("--all", "show_all", is_flag=True, help="Show inactive tokens too")
@click.option("--limit", default=100, help="Maximum number of tokens to return")
def list_tokens(
    api_key: str | None,
    gateway_url: str | None,
    org_id: str | None,
    show_all: bool,
    limit: int,
):
    """List all Personal Access Tokens"""
    client = get_client(api_key, gateway_url, org_id)

    try:
        tokens_list = client.list_tokens(only_active=not show_all, limit=limit)

        if not tokens_list:
            click.echo("No tokens found")
            return

        click.echo(f"\n{len(tokens_list)} token(s):\n")

        for token in tokens_list:
            is_active = token.get("is_active", True)
            status_icon = click.style("✓", fg="green") if is_active else click.style("✗", fg="red")

            scope = token.get("scope", "").replace("environments:", "")
            scope_color = {"admin": "yellow", "execute": "cyan"}.get(scope, "white")

            short_id = token["id"][-12:]
            time_ago = format_relative_time(token["created_at"])

            click.echo(f"{status_icon} {click.style(token['name'], bold=True)}")
            click.echo(f"  {click.style(scope, fg=scope_color)} • {time_ago} • {click.style(short_id, dim=True)}")

            usage = token.get("usage_count", 0)
            if usage > 0:
                last_used = format_relative_time(token.get("last_used_at"))
                click.echo(f"  Used {usage} time(s), last: {last_used}")

            click.echo()

    except Exception as e:
        raise click.ClickException(f"Failed to list tokens: {e}") from e


@tokens.command()
@click.argument("token_id")
@click.option("--api-key", help="Gateway API key (overrides config)")
@click.option("--gateway-url", help="Gateway base URL (overrides config)")
def get(token_id: str, api_key: str | None, gateway_url: str | None):
    """Get details for a specific token"""
    client = get_client(api_key, gateway_url)

    try:
        result = client.get_token(token_id)
        token = result.get("token", result)

        is_active = token.get("is_active")
        status_color = "green" if is_active else "red"
        status_text = "active" if is_active else "revoked"

        click.echo("\n" + "=" * 80)
        print_kv("ID:", token["id"])
        print_kv("Name:", token["name"])
        print_kv("Scope:", token["scope"])
        print_kv("Status:", status_text, color=status_color)
        print_kv("Created:", token["created_at"])
        print_kv("Created by:", token.get("created_by", "N/A"))
        print_kv("Expires:", token.get("expires_at"))
        print_kv("Last used:", token.get("last_used_at"))
        print_kv("Usage count:", token.get("usage_count", 0))

        envs = token.get("allowed_environments")
        env_str = ", ".join(envs) if envs else "All"
        print_kv("Allowed envs:", env_str)

        if token.get("revoked_at"):
            print_kv("Revoked:", token["revoked_at"])
            print_kv("Revoked by:", token.get("revoked_by"))
            print_kv("Reason:", token.get("revocation_reason"))

        click.echo("=" * 80 + "\n")

    except Exception as e:
        raise click.ClickException(f"Failed to get token: {e}") from e


@tokens.command()
@click.argument("token_id")
@click.option("--api-key", help="Gateway API key (overrides config)")
@click.option("--gateway-url", help="Gateway base URL (overrides config)")
@click.option("--name", help="New name for the token")
@click.option("--scope", type=click.Choice(["read", "execute", "admin"]), help="New scope")
@click.option("--env", "environment_ids", multiple=True, help="New environment restrictions")
@click.option("--expires", help="New expiration date (ISO 8601 format)")
def rotate(
    token_id: str,
    api_key: str | None,
    gateway_url: str | None,
    name: str | None,
    scope: str | None,
    environment_ids: tuple[str, ...],
    expires: str | None,
):
    """Rotate a token (generates new token value, revokes old one)"""
    client = get_client(api_key, gateway_url)

    click.echo(f"Rotating token {click.style(token_id, bold=True)}...")

    try:
        result = client.rotate_token(
            token_id=token_id,
            name=name,
            scope=scope,
            environment_ids=list(environment_ids) if environment_ids else None,
            expires_at=expires,
        )

        click.echo("\n" + "=" * 80)
        print_kv("Token ID:", result["id"], color="green")
        print_kv("Name:", result["name"])
        print_kv("Scope:", result["scope"])

        click.echo("\n" + "─" * 80)
        click.echo(f"  {click.style('New Token (save this - shown only once):', fg='yellow', bold=True)}")
        click.echo(f"  {click.style(result['token'], fg='cyan', bold=True)}")
        click.echo("=" * 80)
        click.echo("\n✓ Token rotated successfully (old token revoked)")

    except Exception as e:
        raise click.ClickException(f"Failed to rotate token: {e}") from e


@tokens.command()
@click.argument("token_id")
@click.option("--api-key", help="Gateway API key (overrides config)")
@click.option("--gateway-url", help="Gateway base URL (overrides config)")
@click.option("--reason", help="Reason for revocation")
@click.confirmation_option(prompt="Are you sure you want to revoke this token?")
def revoke(token_id: str, api_key: str | None, gateway_url: str | None, reason: str | None):
    """Revoke a token (cannot be undone)"""
    client = get_client(api_key, gateway_url)

    click.echo(f"Revoking token {click.style(token_id, bold=True)}...")

    try:
        client.revoke_token(token_id=token_id, reason=reason)
        click.echo("\n✓ Token revoked successfully")

    except Exception as e:
        raise click.ClickException(f"Failed to revoke token: {e}") from e
