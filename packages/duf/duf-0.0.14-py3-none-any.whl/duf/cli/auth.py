import uuid
import json
import getpass
import datetime
import subprocess
from pathlib import Path

import jwt
import click
from fans.logger import get_logger

from .api import api
from .cons import paths


logger = get_logger(__name__)


@click.group()
def auth():
    """Authorization"""
    pass


@auth.command()
@click.option('-e', '--expire-seconds', type=int, default=3600)
def login(expire_seconds):
    """Login and save token"""
    username = input('Username: ')
    password = getpass.getpass()
    data = api.post('https://auth.fans656.me/api/login', {
        'username': username,
        'password': password,
        'expire_seconds': expire_seconds,
    })
    if data:
        paths.token.ensure_parent()
        with paths.token.open('w') as f:
            f.write(data['token'])
        click.echo(f'Login succeed (token written in {paths.token})')
    else:
        exit(1)


@auth.command()
def status():
    """Show login status"""
    if paths.token.exists():
        if not paths.public_key.exists():
            res = api.get('https://auth.fans656.me/public-key', raw=True)
            if res.status_code == 200:
                with paths.public_key.open('w') as f:
                    f.write(res.text)
            else:
                click.echo(click.style('failed to get public key', fg='red'))
                exit(1)
        with paths.public_key.open() as f:
            public_key = f.read()
        with paths.token.open() as f:
            token = f.read()
        data = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            options={"verify_signature": False, "verify_exp": False},
        )
        click.echo('-' * 80 + 'public key')
        click.echo(public_key)
        click.echo('-' * 80 + 'token')
        click.echo(token)
        click.echo('-' * 80 + 'decoded')
        click.echo(json.dumps(data, indent=2))
        if 'exp' in data:
            exp = datetime.datetime.fromtimestamp(data['exp'])
            exp_str = exp.strftime('%Y-%m-%d %H:%M:%S')
            message = f'Expiration {exp_str}'
            if exp <= datetime.datetime.now():
                message = click.style(message, fg='red')
            click.echo(message)
    else:
        click.echo(click.style('not logged in', fg='red'))
