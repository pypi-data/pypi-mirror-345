import click

from .log import log
from .init import init
from .host import host
from .auth import auth
from .deploy import deploy
from .utils import execute


@click.group
def cli():
    pass


cli.add_command(init)
cli.add_command(host)
cli.add_command(auth)
cli.add_command(deploy)
cli.add_command(log)


@cli.command
def publish():
    execute('uv build')
    execute('uv publish')
    execute('rm -r dist *.egg-info')
