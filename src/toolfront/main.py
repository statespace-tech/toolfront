import click

from .cli.deploy import deploy
from .cli.mcp import mcp
from .cli.serve import serve


@click.group()
def main():
    """ToolFront CLI"""
    pass


main.add_command(serve)
main.add_command(mcp)
main.add_command(deploy)

if __name__ == "__main__":
    main()
