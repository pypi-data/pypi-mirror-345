import os
import json

import click
import requests

from .cons import paths


class API:

    def __init__(self):
        self.origin = 'https://duf.fans656.me'

    def get(self, *args, **kwargs):
        return self.request('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request('POST', *args, **kwargs)

    def request(self, method, path, req: dict = {}, raw: bool = False):
        if path.startswith('http'):
            url = path
        else:
            url = f'{self.origin}{path}'

        cookies = {}
        if paths.token.exists():
            with paths.token.open() as f:
                cookies['token'] = f.read()

        if method == 'GET':
            res = requests.get(
                url,
                params=req,
                cookies=cookies,
            )
        else:
            res = requests.post(
                url,
                json=req,
                cookies=cookies,
            )

        if res.status_code == 200:
            if raw:
                return res
            else:
                return res.json()
        else:
            try:
                click.echo(json.dumps(res.json(), indent=2))
            except:
                click.echo(res.text)
            click.echo(click.style(f'ERROR: {res.status_code}', fg='red'))


api = API()
