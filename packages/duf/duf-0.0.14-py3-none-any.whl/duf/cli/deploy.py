import json
import subprocess
from pathlib import Path

import click
from fans.logger import get_logger

from .api import api


logger = get_logger(__name__)


@click.command()
@click.option('-S', '--no-sync', is_flag=True)
def deploy(no_sync):
    """Deploy current project"""
    cwd = Path().absolute()
    proj_name = cwd.name
    host = get_target_host()

    #execute(f"ssh root@{host['ip']} 'curl -s https://duf.fans656.me/init-duf.sh | bash'")

    if not no_sync:
        execute([
            f"rsync -rav",

            f"--exclude '**/__pycache__/'",
            f"--exclude '**/node_modules/'",

            f"--include '{proj_name}/'",
            f"--include '{proj_name}/**'",

            f"--include 'frontend/'",
            f"--include 'frontend/dist/'",
            f"--include 'frontend/dist/**'",

            f"--include 'scripts/'",
            f"--include 'scripts/**'",

            f"--include 'pyproject.toml'",
            f"--include 'uv.lock'",
            f"--include 'serve.sh'",

            f"--exclude '*'",

            f"./ root@{host['ip']}:/root/{proj_name}",
        ])

    execute(
        f"ssh root@{host['ip']} "
        f"uv --directory /root/duf run -m "
        f"duf.cli.on_host_deploy --target /root/{proj_name}"
    )
    #execute(f"ssh root@{host['ip']} supervisorctl restart {proj_name}")


def get_target_host():
    cache_json = Path('./.duf-cache.json')
    if not cache_json.exists():
        with cache_json.open('w') as f:
            json.dump({}, f)

    with cache_json.open() as f:
        data = json.load(f)
        if 'host' in data:
            return data['host']

    logger.info('getting target host to deploy...')
    data = api.post('/api/host/ls')
    if data:
        for host in data['hosts']:
            if host.get('name') == 'default':
                logger.info(f'got target host {host}')

                data['host'] = host
                with cache_json.open('w') as f:
                    json.dump(data, f, indent=2)

                return host
    logger.error('failed to get target host to deploy')
    exit(1)


def execute(cmd: str|list[str]):
    if isinstance(cmd, list):
        cmd = ' '.join(cmd)
    logger.info(f'[CMD] {cmd}')
    proc = subprocess.run(cmd, shell=True)
    if not proc.returncode == 0:
        logger.error(f'failed to execute command: {cmd}')
        exit(1)
