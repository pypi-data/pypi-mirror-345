from fans.path import Path, make_paths


_server_dir = Path(__file__).parent
_duf_dir = _server_dir.parent
_proj_root_dir = _duf_dir.parent


class Env:

    def __init__(self):
        self.reset()

    def reset(self, root = ''):
        self.paths = make_paths([
            Path(root), [
                'data', [
                    'hosts.json', {'hosts'},
                ],
            ],
            _proj_root_dir, [
                'scripts', [
                    'init-duf.sh', {'init_duf_sh'},
                ],
            ],
        ])


env = Env()
