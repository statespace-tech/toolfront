import click

from .cli.database import database
from .cli.mcp import mcp


@click.group()
def main():
    """ToolFront CLI"""
    pass


main.add_command(mcp)
main.add_command(database)

if __name__ == "__main__":
    main()
