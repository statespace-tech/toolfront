import click
from datetime import datetime

from toolfront.lib.config import get_api_credentials
from toolfront.lib.gateway import GatewayClient


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
@click.option("--env", "environment_ids", multiple=True, help="Restrict to specific environment IDs (can be used multiple times)")
@click.option("--expires", help="Expiration date (ISO 8601 format, e.g., 2025-12-31T23:59:59Z)")
def create(name: str, api_key: str | None, gateway_url: str | None, org_id: str | None, scope: str, environment_ids: tuple[str, ...], expires: str | None):
    """Create a new Personal Access Token"""
    try:
        gateway_url, api_key, org_id = get_api_credentials(api_key, gateway_url, org_id)
    except ValueError as e:
        raise click.ClickException(str(e)) from e

    client = GatewayClient(gateway_url, api_key, org_id)

    click.echo(f"Creating token '{click.style(name, bold=True)}'...")

    try:
        result = client.create_token(
            name=name,
            scope=scope,
            environment_ids=list(environment_ids) if environment_ids else None,
            expires_at=expires,
        )

        click.echo("\n" + "=" * 80)
        click.echo(f"  Token ID:    {click.style(result['id'], fg='green')}")
        click.echo(f"  Name:        {result['name']}")
        click.echo(f"  Scope:       {result['scope']}")
        click.echo(f"  Created:     {result['created_at']}")
        if result.get('expires_at'):
            click.echo(f"  Expires:     {result['expires_at']}")
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
def list_tokens(api_key: str | None, gateway_url: str | None, org_id: str | None, show_all: bool, limit: int):
    """List all Personal Access Tokens"""
    try:
        gateway_url, api_key, org_id = get_api_credentials(api_key, gateway_url, org_id)
    except ValueError as e:
        raise click.ClickException(str(e)) from e

    client = GatewayClient(gateway_url, api_key, org_id)

    try:
        tokens_list = client.list_tokens(only_active=not show_all, limit=limit)

        if not tokens_list:
            click.echo("No tokens found")
            return

        click.echo(f"\nFound {len(tokens_list)} token(s):\n")
        click.echo("─" * 100)
        click.echo(f"{'ID':<38} {'NAME':<25} {'SCOPE':<10} {'STATUS':<10} {'CREATED'}")
        click.echo("─" * 100)

        for token in tokens_list:
            status = "active" if token.get('is_active', True) else "revoked"
            status_color = 'green' if status == "active" else 'red'
            created = token['created_at'].split('T')[0]

            click.echo(
                f"{token['id']:<38} "
                f"{token['name'][:24]:<25} "
                f"{token['scope']:<10} "
                f"{click.style(status, fg=status_color):<19} "
                f"{created}"
            )

        click.echo("─" * 100)

    except Exception as e:
        raise click.ClickException(f"Failed to list tokens: {e}") from e


@tokens.command()
@click.argument("token_id")
@click.option("--api-key", help="Gateway API key (overrides config)")
@click.option("--gateway-url", help="Gateway base URL (overrides config)")
def get(token_id: str, api_key: str | None, gateway_url: str | None):
    """Get details for a specific token"""
    try:
        gateway_url, api_key, _ = get_api_credentials(api_key, gateway_url)
    except ValueError as e:
        raise click.ClickException(str(e)) from e

    client = GatewayClient(gateway_url, api_key)

    try:
        result = client.get_token(token_id)
        token = result.get('token', result)

        click.echo("\n" + "=" * 80)
        click.echo(f"  ID:              {token['id']}")
        click.echo(f"  Name:            {token['name']}")
        click.echo(f"  Scope:           {token['scope']}")
        click.echo(f"  Status:          {click.style('active' if token.get('is_active') else 'revoked', fg='green' if token.get('is_active') else 'red')}")
        click.echo(f"  Created:         {token['created_at']}")
        click.echo(f"  Created by:      {token.get('created_by', 'N/A')}")

        if token.get('expires_at'):
            click.echo(f"  Expires:         {token['expires_at']}")

        if token.get('last_used_at'):
            click.echo(f"  Last used:       {token['last_used_at']}")

        click.echo(f"  Usage count:     {token.get('usage_count', 0)}")

        if token.get('allowed_environments'):
            click.echo(f"  Allowed envs:    {', '.join(token['allowed_environments'])}")
        else:
            click.echo(f"  Allowed envs:    All")

        if token.get('revoked_at'):
            click.echo(f"  Revoked:         {token['revoked_at']}")
            if token.get('revoked_by'):
                click.echo(f"  Revoked by:      {token['revoked_by']}")
            if token.get('revocation_reason'):
                click.echo(f"  Reason:          {token['revocation_reason']}")

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
def rotate(token_id: str, api_key: str | None, gateway_url: str | None, name: str | None, scope: str | None, environment_ids: tuple[str, ...], expires: str | None):
    """Rotate a token (generates new token value, revokes old one)"""
    try:
        gateway_url, api_key, _ = get_api_credentials(api_key, gateway_url)
    except ValueError as e:
        raise click.ClickException(str(e)) from e

    client = GatewayClient(gateway_url, api_key)

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
        click.echo(f"  Token ID:    {click.style(result['id'], fg='green')}")
        click.echo(f"  Name:        {result['name']}")
        click.echo(f"  Scope:       {result['scope']}")
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
    try:
        gateway_url, api_key, _ = get_api_credentials(api_key, gateway_url)
    except ValueError as e:
        raise click.ClickException(str(e)) from e

    client = GatewayClient(gateway_url, api_key)

    click.echo(f"Revoking token {click.style(token_id, bold=True)}...")

    try:
        client.revoke_token(token_id=token_id, reason=reason)
        click.echo(f"\n✓ Token revoked successfully")

    except Exception as e:
        raise click.ClickException(f"Failed to revoke token: {e}") from e
