import uvicorn
from fans.ports import ports

from fansauth import cons
from fansauth.server.env import env
from fansauth.server.app import app


if __name__ == '__main__':
    env.setup(cons.root_dir / 'data')
    uvicorn.run(app, host='0.0.0.0', port=ports.auth_back)
