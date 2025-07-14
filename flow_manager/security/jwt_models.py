from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, AnyHttpUrl


class TokenPayload(BaseModel):
    sub: str
    scope: str
    iss: AnyHttpUrl
    aud: str
    exp: datetime
    nbf: datetime
    iat: datetime
