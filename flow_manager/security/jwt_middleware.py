from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Awaitable, Callable, cast

import httpx
from aiocache import Cache, cached
from fastapi import Request, Response
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from .jwt_models import TokenPayload

SKEW = timedelta(seconds=60)

_SCOPE_TABLE: dict[str, str] = {
    "/flowmanager/topology_update": "topology:write",
    "/flowmanager/packetin": "packetin:write",
    "/api/v1/flows": "flows:write",
    "/peer/v1/flows": "flows:write",
}


@cached(ttl=600, cache=Cache.MEMORY)  # type: ignore[misc]
async def fetch_jwks(jwks_url: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(jwks_url, timeout=3)
        return cast(dict[str, Any], resp.json())


def _extract_bearer(header: str | None) -> str | None:
    if not header or not header.startswith("Bearer "):
        return None
    return header.split()[1]


def _required_scope(path: str) -> str | None:
    for prefix, scope in _SCOPE_TABLE.items():
        if path.startswith(prefix):
            return scope
    return None


def _unauth(detail: str) -> Response:
    body = json.dumps({"detail": detail})
    return Response(
        body, status_code=HTTP_401_UNAUTHORIZED, media_type="application/json"
    )


def _forbidden(detail: str) -> Response:
    body = json.dumps({"detail": detail})
    return Response(body, status_code=HTTP_403_FORBIDDEN, media_type="application/json")


class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Any, jwks_url: str) -> None:
        super().__init__(app)
        self.jwks_url = jwks_url

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        token = _extract_bearer(request.headers.get("Authorization"))
        if not token:
            return _unauth("missing bearer")

        try:
            jwks = await fetch_jwks(self.jwks_url)
            payload = jwt.decode(
                token, jwks, algorithms=["ES256"], audience="flow-manager"
            )
            claims = TokenPayload(**payload)
            now = datetime.now(timezone.utc)
            if not (claims.nbf - SKEW <= now <= claims.exp + SKEW):
                raise JWTError("token expired or not yet valid")
        except JWTError as exc:
            return _unauth(str(exc))

        expected = _required_scope(request.url.path)
        if expected and expected not in claims.scope.split():
            return _forbidden(f"scope '{expected}' required")

        request.state.jwt_payload = claims.dict()
        return await call_next(request)
