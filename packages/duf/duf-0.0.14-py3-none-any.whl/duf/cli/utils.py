import subprocess

from fans.logger import get_logger


logger = get_logger(__name__)


def execute(cmd: str|list[str]):
    if isinstance(cmd, list):
        cmd = ' '.join(cmd)
    logger.info(f'[CMD] {cmd}')
    proc = subprocess.run(cmd, shell=True)
    if not proc.returncode == 0:
        logger.error(f'failed to execute command: {cmd}')
        exit(1)
