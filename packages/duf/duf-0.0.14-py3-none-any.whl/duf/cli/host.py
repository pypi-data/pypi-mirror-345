import os
import json
import uuid
import subprocess
from pathlib import Path

import yaml
import click

from .api import api


@click.group()
def host():
    """Host management"""
    pass


@host.command()
def ls():
    """List available hosts"""
    data = api.post('/api/host/ls')
    if data:
        for host in data['hosts']:
            click.echo(f'{host}')


@host.command()
@click.argument('name')
def add(name: str):
    """Add new host"""
    data = api.post('/api/host/add', {'name': name})
    if data:
        click.echo(f'Added {data}')


@host.command()
@click.argument('target')
def edit(target: str):
    """Edit host info"""
    old_data = api.post('/api/host/info', {'target': target})
    if not old_data:
        return
    fpath = Path('DUF_TARGET_EDITING')
    try:
        with fpath.open('w') as f:
            yaml.dump(old_data, f)

        editor = os.getenv('EDITOR', 'vi')
        subprocess.run(f'{editor} {fpath}', shell=True)

        with fpath.open() as f:
            new_data = yaml.safe_load(f)

        if old_data == new_data:
            click.echo('Nothing changed')
        else:
            api.post('/api/host/edit', new_data)
    finally:
        if fpath.exists():
            fpath.unlink()


@host.command()
@click.argument('target')
def info(target: str):
    """Show host info"""
    host = api.post('/api/host/info', {'target': target})
    if host:
        click.echo(json.dumps(host, indent=2))


@host.command()
@click.argument('target')
def rm(target: str):
    """Remove host"""
    data = api.post('/api/host/remove', {'target': target})
    if data:
        click.echo(f'Removed {data["id"]}')
