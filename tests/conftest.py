import datetime as dt
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from jose import jwt


def make_jwt(scope: str, ttl: int = 60) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": "test",
        "scope": scope,
        "iat": int(now.timestamp()),
        "exp": int((now + dt.timedelta(seconds=ttl)).timestamp()),
    }
    return jwt.encode(payload, "secret", algorithm="HS256")


__all__ = ["make_jwt"]
