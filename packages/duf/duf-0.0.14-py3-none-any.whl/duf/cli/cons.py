from fans.path import Path, make_paths


paths = make_paths(
    Path.home(), [
        '.duf', [
            'auth', [
                'token', {'token'},
                'public_key', {'public_key'},
            ],
        ],
    ],
)
