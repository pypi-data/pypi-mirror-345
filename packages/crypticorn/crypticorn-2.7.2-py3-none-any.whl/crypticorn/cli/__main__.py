# crypticorn/cli.py

import click
from crypticorn.cli import init_group


@click.group()
def cli():
    """🧙 Crypticorn CLI — magic for our microservices."""
    pass


cli.add_command(init_group, name="init")

if __name__ == "__main__":
    cli()
