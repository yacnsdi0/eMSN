"""JWT authentication middleware."""
from __future__ import annotations

from typing import Any, Callable

import jwt
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jwt import PyJWKClient


JWKS_URL = "https://nrf.local/.well-known/jwks.json"
AUDIENCE = "flow-manager"


class JWTMiddleware(BaseHTTPMiddleware):
    """Validate JWT tokens and check scopes."""

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self.jwk_client = PyJWKClient(JWKS_URL)

    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="missing token")
        token = auth.split()[1]
        try:
            signing_key = self.jwk_client.get_signing_key_from_jwt(token).key
            payload = jwt.decode(token, signing_key, algorithms=["ES256"], audience=AUDIENCE)
        except Exception as exc:  # pragma: no cover - network/crypto errors
            raise HTTPException(status_code=401, detail="invalid token") from exc
        scopes = payload.get("scope", "").split()
        path = request.url.path
        if path.startswith("/flowmanager/topology_update") and "topology:write" not in scopes:
            raise HTTPException(status_code=403, detail="missing scope")
        if path.startswith("/flowmanager/packetin") and "packetin:write" not in scopes:
            raise HTTPException(status_code=403, detail="missing scope")
        if path.startswith("/api/v1/flows") and "flows:write" not in scopes:
            raise HTTPException(status_code=403, detail="missing scope")
        return await call_next(request)
