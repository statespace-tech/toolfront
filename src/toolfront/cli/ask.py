import click

from toolfront.application import Application


@click.command()
@click.argument("url", type=click.STRING)
@click.argument("prompt", type=click.STRING)
@click.option("--model", type=click.STRING, default=None, help="AI model to use")
@click.option(
    "--param", type=click.STRING, default=None, help="Authentication parameter for the remote application: KEY=VALUE"
)
@click.option("--env", type=click.STRING, default=None, help="Environment variables to pass to commands (KEY=VALUE)")
@click.option("--verbose", is_flag=True, help="Show verbose output")
def ask(url: str, prompt: str, model: str | None, param: str | None, env: str | None, verbose: bool = False) -> None:
    """Ask a question to the application"""
    try:
        application = Application(url=url, param=param, env=env)
        response = application.ask(prompt, model=model, verbose=verbose)
        click.echo(response)
    except RuntimeError as e:
        raise click.ClickException(str(e)) from e
