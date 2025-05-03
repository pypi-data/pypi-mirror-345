import json
import datetime

import jwt

from fansauth.server import utils


class User:

    def __init__(self, model, private_key: bytes):
        self.model = model
        self.private_key = private_key

        self.username = self.model.username
        self.meta = json.loads(self.model.meta)
        self.extra = json.loads(self.model.extra)

    def verify_password(self, password: str) -> bool:
        got_pwd = utils.hashed_password(password, self.model.salt)
        exp_pwd = self.model.hashed_password
        return got_pwd == exp_pwd

    @property
    def access_token(self) -> str:
        token = self.generate_access_token()
        return token.raw

    def generate_access_token(self, expire_seconds: int = 0):
        return AccessToken(
            {
                'username': self.username,
                'admin': self.is_admin(),
            },
            private_key=self.private_key,
            expire_seconds=expire_seconds,
        )

    def is_admin(self) -> bool:
        return self.meta.get('admin') == True

    def __str__(self):
        return f'User(username={self.model.username})'


class AccessToken:

    def __init__(
            self,
            data,
            private_key: bytes,
            expire_seconds: int = 0,
    ):
        self.data = data
        self.expire_seconds = expire_seconds or 30 * 24 * 3600  # 30 days by default

        now = datetime.datetime.now(datetime.UTC)
        self.data.update({
            'exp': int((now + datetime.timedelta(seconds=expire_seconds)).timestamp()),
        })

        self.raw = jwt.encode(data, private_key, algorithm='RS256')

    def as_dict(self):
        return {
            'token': self.raw,
            'expire_seconds': self.expire_seconds,
        }
