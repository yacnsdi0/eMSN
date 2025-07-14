class JWTError(Exception):
    pass


from . import jwt as jwt  # noqa: E402

__all__ = ["jwt", "JWTError"]
