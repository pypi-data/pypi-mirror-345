import subprocess
from pathlib import Path

import click
from fans.logger import get_logger

from .api import api


logger = get_logger(__name__)


@click.command()
def log():
    """Show running instance log"""
    pass
    #os.system('')
