import click

from .cli.delete import delete
from .cli.deploy import deploy
from .cli.list import list_deployments
from .cli.mcp import mcp
from .cli.serve import serve
from .cli.tokens import tokens
from .cli.update import update


@click.group()
def main():
    """ToolFront CLI"""
    pass


main.add_command(serve)
main.add_command(mcp)
main.add_command(deploy)
main.add_command(list_deployments, name="list")
main.add_command(update)
main.add_command(delete)
main.add_command(tokens)

if __name__ == "__main__":
    main()
