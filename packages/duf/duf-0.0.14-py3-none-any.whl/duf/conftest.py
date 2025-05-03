import pytest
from starlette.testclient import TestClient

from duf.server.app import app
from duf.server.env import env


@pytest.fixture
def client(tmp_path):
    env.reset(root=tmp_path)
    yield TestClient(app)
