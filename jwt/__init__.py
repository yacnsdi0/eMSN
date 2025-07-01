import base64
import json

class PyJWKClient:
    def __init__(self, url: str):
        self.url = url
    def get_signing_key_from_jwt(self, token: str):
        class Key:
            def __init__(self):
                self.key = 'dummy'
        return Key()

def decode(token: str, key: str | None = None, algorithms=None, audience: str | None = None):
    try:
        header, payload, _ = token.split('.')
        padded = payload + '=' * (-len(payload) % 4)
        data = base64.urlsafe_b64decode(padded)
        return json.loads(data)
    except Exception as e:
        raise Exception('decode error') from e
