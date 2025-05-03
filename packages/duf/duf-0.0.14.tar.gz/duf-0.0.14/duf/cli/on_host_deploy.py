import os
from pathlib import Path

import click


@click.command
@click.option('-t', '--target')
def cli(target):
    proj_dir = Path(target)
    print(f'project directory: {proj_dir}')
    proj_name = proj_dir.name
    print(f'project name: {proj_name}')
    supervisor_conf_path = Path(f'/etc/supervisor/conf.d/{proj_name}.conf')

    if not supervisor_conf_path.exists():
        with supervisor_conf_path.open('w') as f:
            f.write(supervisor_conf_template.format(
                proj_name=proj_name,
            ))
        print(f'written supervisor conf: {supervisor_conf_path}')

        execute('supervisorctl reread')
        execute('supervisorctl update')

    execute(f'supervisorctl restart {proj_name}')


def execute(cmd):
    print(f'[CMD] {cmd}')
    os.system(cmd)


supervisor_conf_template = '''
[program:{proj_name}]
command=/root/{proj_name}/serve.sh
directory=/root/{proj_name}
autostart=true
autorestart=true
stderr_logfile=/var/log/{proj_name}.err.log
stdout_logfile=/var/log/{proj_name}.out.log
stopasgroup=true
killasgroup=True
'''


if __name__ == '__main__':
    cli()
