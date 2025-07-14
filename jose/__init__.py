from . import jwt as jwt

__all__ = ["jwt", "JWTError"]


class JWTError(Exception):
    pass
