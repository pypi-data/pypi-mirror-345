import uvicorn
from fans.ports import ports

from .app import app


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=ports.duf_back)
