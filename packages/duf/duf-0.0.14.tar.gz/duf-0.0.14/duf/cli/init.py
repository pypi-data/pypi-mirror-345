import click

from .utils import execute


@click.group()
def init():
    """Initialize project"""
    pass


@init.command()
def frontend():
    """Initialize frontend"""
    execute('npm create vite@latest -y frontend -- --template react')
